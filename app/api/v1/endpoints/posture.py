# app/api/v1/endpoints/posture.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from app.core.config import settings
from app.utils.files import allowed_file, secure_filename
from app.services import storage
from app.services.ergonomics import analyze
from app.api.deps import get_db
from app.models import Posture  # model
from app.services.db_helpers import get_or_create_user, coerce_results_for_posture
from app.services.supabase_storage import upload_bytes  # ← NEW

logger = logging.getLogger("ergokey")
router = APIRouter()

@router.post("/posture")
async def upload_posture(
    email: str = Form(...),
    capture_id: str = Form(...),
    front_image: UploadFile = File(...),
    side_image: UploadFile = File(...),
    overhead_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email valid diperlukan")
    if not capture_id:
        raise HTTPException(status_code=400, detail="capture_id diperlukan")

    for f in (front_image, side_image, overhead_image):
        if not f.filename or not allowed_file(f.filename):
            raise HTTPException(status_code=400, detail=f"File tidak valid: {f.filename}")

    storage.ensure_dirs()
    user_dir = settings.POSTURE_DIR / f"{email}_posture"
    saved_local: list[str] = []
    supa_urls: dict[str, str | None] = {"front": None, "side": None, "overhead": None}

    async def _save(upload: UploadFile, label: str):
        # 1) read bytes
        raw = await upload.read()

        # 2) save local
        ext = Path(upload.filename).suffix.lower()
        name = secure_filename(f"{capture_id}_{label}_image{ext}")
        path = user_dir / name
        storage.save_bytes(path, raw)
        # simpan path lokal (boleh relative ke STORAGE_ROOT biar rapi)
        try:
            saved_local.append(str(path.relative_to(settings.STORAGE_ROOT)))
        except Exception:
            saved_local.append(str(path))

        # 3) upload ke Supabase (remote: email/capture_id_label_image.ext)
        try:
            remote_path = f"{email}/{name}"
            url = upload_bytes(
                bucket=settings.SUPABASE_BUCKET or "posture",
                remote_path=remote_path,
                data=raw,
                filename_hint=name,
                upsert=True,
            )
            supa_urls[label] = url
        except Exception as e:
            # Jangan gagalkan request hanya karena upload supabase gagal
            logger.error("Supabase upload gagal untuk %s: %s", label, e, exc_info=True)

        return raw

    front = await _save(front_image, "front")
    side  = await _save(side_image,  "side")
    over  = await _save(overhead_image, "overhead")

    # 4) analisis
    try:
        results = analyze(front, side, over)
    except RuntimeError as e:
        return JSONResponse(status_code=422, content={"status": "error", "message": str(e)})

    if not results:
        return JSONResponse(status_code=422, content={"status":"error","message":"Analisis gagal"})

    # 5) SIMPAN KE DB (pakai URL Supabase jika ada)
    get_or_create_user(db, email=email)

    existing = db.query(Posture).filter(
        Posture.user_email == email,
        Posture.capture_id == capture_id
    ).one_or_none()

    mapped = coerce_results_for_posture(results)

    # pilih link: supabase kalau ada, fallback ke lokal
    front_link = supa_urls["front"] or (saved_local[0] if len(saved_local) > 0 else None)
    side_link  = supa_urls["side"]  or (saved_local[1] if len(saved_local) > 1 else None)
    over_link  = supa_urls["overhead"] or (saved_local[2] if len(saved_local) > 2 else None)

    if existing:
        existing.front_image_link = front_link or existing.front_image_link
        existing.side_image_link = side_link or existing.side_image_link
        existing.overhead_image_link = over_link or existing.overhead_image_link
        for k, v in mapped.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
    else:
        payload = {
            "user_email": email,
            "capture_id": capture_id,
            "front_image_link": front_link,
            "side_image_link":  side_link,
            "overhead_image_link": over_link,
        }
        payload.update({k: v for k, v in mapped.items() if hasattr(Posture, k)})
        db.add(Posture(**payload))

    db.commit()

    # 6) log lokal (opsional, biar kompatibel dgn pipeline lama)
    storage.update_user_history(email, capture_id, results)
    storage.update_global_average(results)

    return {
        "status":"success",
        "message":"Berhasil",
        "data":{
            "saved_local": saved_local,
            "supabase": {
                "front": supa_urls["front"],
                "side":  supa_urls["side"],
                "overhead": supa_urls["overhead"],
            },
            "analysis_results": results
        }
    }
