# app/api/v1/endpoints/posture.py
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from app.core.config import settings
from app.utils.files import allowed_file, secure_filename
from app.services import storage
from app.services.ergonomics import analyze
from app.api.deps import get_db, get_current_email, ensure_same_email, get_principal, Principal
from app.models import Posture  # model
from app.services.db_helpers import get_or_create_user, coerce_results_for_posture
from app.services.supabase_storage import upload_bytes, default_bucket, signed_url

logger = logging.getLogger("ergokey")
router = APIRouter()

_LABELS = ("front", "side", "overhead")
_upload_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="supabase-upload")


def _read_image(upload: UploadFile) -> bytes:
    if not upload.filename or not allowed_file(upload.filename):
        raise HTTPException(status_code=400, detail=f"File tidak valid: {upload.filename}")
    raw = upload.file.read(settings.MAX_IMAGE_BYTES + 1)
    if len(raw) > settings.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail=f"File terlalu besar: {upload.filename}")
    if not raw:
        raise HTTPException(status_code=400, detail=f"File kosong: {upload.filename}")
    return raw


def _upload_remote(remote_path: str, raw: bytes, name: str, label: str) -> str | None:
    try:
        return upload_bytes(
            bucket=default_bucket(),
            remote_path=remote_path,
            data=raw,
            filename_hint=name,
            upsert=True,
        )
    except Exception as e:
        # Jangan gagalkan request hanya karena upload supabase gagal
        logger.error("Supabase upload gagal untuk %s: %s", label, e, exc_info=True)
        return None


# `def` (bukan async): analisis gambar, upload & query DB semuanya blocking,
# jadi biarkan FastAPI menjalankannya di threadpool.
@router.post("/posture")
def upload_posture(
    capture_id: str = Form(..., min_length=1, max_length=100),
    front_image: UploadFile = File(...),
    side_image: UploadFile = File(...),
    overhead_image: UploadFile = File(...),
    email: str | None = Form(None),
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_email),
):
    email = ensure_same_email(user_email, email)
    capture_id = secure_filename(capture_id)

    images = {
        "front": _read_image(front_image),
        "side": _read_image(side_image),
        "overhead": _read_image(overhead_image),
    }
    uploads = {"front": front_image, "side": side_image, "overhead": overhead_image}

    storage.ensure_dirs()
    user_dir = storage.user_posture_dir(email)
    remote_dir = user_dir.name.removesuffix("_posture")
    saved_local: dict[str, str] = {}
    futures = {}

    for label in _LABELS:
        raw = images[label]
        ext = Path(uploads[label].filename).suffix.lower()
        name = secure_filename(f"{capture_id}_{label}_image{ext}")
        path = user_dir / name
        storage.save_bytes(path, raw)
        saved_local[label] = str(path.relative_to(settings.STORAGE_ROOT))
        # upload ke Supabase paralel dengan analisis
        futures[label] = _upload_pool.submit(_upload_remote, f"{remote_dir}/{name}", raw, name, label)

    # analisis
    try:
        results = analyze(images["front"], images["side"], images["overhead"])
    except RuntimeError as e:
        return JSONResponse(status_code=422, content={"status": "error", "message": str(e)})

    supa_refs = {label: f.result() for label, f in futures.items()}

    if not results:
        return JSONResponse(status_code=422, content={"status":"error","message":"Analisis gagal"})

    # SIMPAN KE DB (pakai referensi Supabase jika ada, fallback ke path lokal)
    get_or_create_user(db, email=email)

    existing = db.query(Posture).filter(
        Posture.user_email == email,
        Posture.capture_id == capture_id
    ).one_or_none()

    mapped = coerce_results_for_posture(results)
    links = {label: supa_refs[label] or saved_local[label] for label in _LABELS}

    if existing:
        existing.front_image_link = links["front"] or existing.front_image_link
        existing.side_image_link = links["side"] or existing.side_image_link
        existing.overhead_image_link = links["overhead"] or existing.overhead_image_link
        for k, v in mapped.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
    else:
        payload = {
            "user_email": email,
            "capture_id": capture_id,
            "front_image_link": links["front"],
            "side_image_link":  links["side"],
            "overhead_image_link": links["overhead"],
        }
        payload.update({k: v for k, v in mapped.items() if hasattr(Posture, k)})
        db.add(Posture(**payload))

    db.commit()

    # log file lokal (pipeline lama, opsional)
    if settings.LEGACY_FILE_LOGS:
        storage.update_user_history(email, capture_id, results)
        storage.update_global_average(results)

    return {
        "status":"success",
        "message":"Berhasil",
        "data":{
            "saved_local": [saved_local[label] for label in _LABELS],
            "supabase": {label: bool(supa_refs[label]) for label in _LABELS},
            "analysis_results": results
        }
    }


@router.get("/posture/{posture_id}/images", summary="Signed URL sementara untuk gambar posture")
def posture_images(
    posture_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_principal),
):
    row = db.get(Posture, posture_id)
    if not row or (not principal.is_admin and row.user_email.lower() != principal.email.lower()):
        raise HTTPException(status_code=404, detail="Posture tidak ditemukan")
    try:
        return {
            "front": signed_url(row.front_image_link),
            "side": signed_url(row.side_image_link),
            "overhead": signed_url(row.overhead_image_link),
            "expires_in": settings.SUPABASE_SIGNED_URL_TTL,
        }
    except Exception:
        logger.exception("Gagal membuat signed URL untuk posture %s", posture_id)
        raise HTTPException(status_code=502, detail="Gagal membuat URL gambar")
