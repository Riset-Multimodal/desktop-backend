# app/services/supabase_storage.py
from functools import lru_cache
from typing import Optional
from urllib.parse import unquote, urlparse
from supabase import create_client, Client
from app.core.config import settings
import mimetypes
import logging

logger = logging.getLogger("ergokey")

# Prefix untuk link gambar yang disimpan di DB. Bucket sebaiknya PRIVATE;
# URL untuk melihat gambar dibuat on-demand lewat signed URL.
STORAGE_SCHEME = "supabase://"

def _guess_content_type(filename: str) -> str:
    ctype, _ = mimetypes.guess_type(filename)
    return ctype or "application/octet-stream"

@lru_cache(maxsize=1)
def _get_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL / SUPABASE_KEY belum dikonfigurasi di .env")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def default_bucket() -> str:
    return settings.SUPABASE_BUCKET or "posture"

def upload_bytes(
    bucket: str,
    remote_path: str,
    data: bytes,
    filename_hint: Optional[str] = None,
    upsert: bool = True,
) -> str:
    """
    Upload bytes ke Supabase storage dan kembalikan referensi object
    (`supabase://<bucket>/<path>`), bukan public URL.
    """
    supa = _get_client()
    content_type = _guess_content_type(filename_hint or remote_path)

    # upsert=True agar overwrite jika nama sama
    opts = {"upsert": "true"} if upsert else {}
    if content_type:
        opts["contentType"] = content_type

    logger.info("[supabase] upload %s -> bucket=%s", remote_path, bucket)
    supa.storage.from_(bucket).upload(remote_path, data, opts)
    return f"{STORAGE_SCHEME}{bucket}/{remote_path}"

def _parse_object_ref(link: str) -> Optional[tuple[str, str]]:
    if link.startswith(STORAGE_SCHEME):
        bucket, _, path = link[len(STORAGE_SCHEME):].partition("/")
        return (bucket, path) if bucket and path else None
    # Data lama: public URL .../storage/v1/object/public/<bucket>/<path>
    marker = "/storage/v1/object/public/"
    parsed = urlparse(link)
    if marker in parsed.path:
        bucket, _, path = parsed.path.split(marker, 1)[1].partition("/")
        return (bucket, unquote(path)) if bucket and path else None
    return None

def signed_url(link: Optional[str]) -> Optional[str]:
    """Buat signed URL sementara dari link yang tersimpan di DB."""
    if not link:
        return None
    ref = _parse_object_ref(link)
    if not ref:
        return None
    bucket, path = ref
    res = _get_client().storage.from_(bucket).create_signed_url(path, settings.SUPABASE_SIGNED_URL_TTL)
    return res.get("signedURL") or res.get("signedUrl") or res.get("signed_url")
