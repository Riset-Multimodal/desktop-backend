# app/services/supabase_storage.py
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings
import mimetypes
import logging

logger = logging.getLogger("ergokey")

def _guess_content_type(filename: str) -> str:
    ctype, _ = mimetypes.guess_type(filename)
    return ctype or "application/octet-stream"

def _get_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL / SUPABASE_KEY belum dikonfigurasi di .env")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_bytes(
    bucket: str,
    remote_path: str,
    data: bytes,
    filename_hint: Optional[str] = None,
    upsert: bool = True,
) -> str:
    """
    Upload bytes ke Supabase storage dan kembalikan public URL.
    """
    supa = _get_client()
    content_type = _guess_content_type(filename_hint or remote_path)

    # upsert=True agar overwrite jika nama sama
    opts = {"upsert": "true"} if upsert else {}
    if content_type:
        opts["contentType"] = content_type

    logger.info("[supabase] upload %s -> bucket=%s", remote_path, bucket)
    supa.storage.from_(bucket).upload(remote_path, data, opts)
    url = supa.storage.from_(bucket).get_public_url(remote_path)
    logger.info("[supabase] public url: %s", url)
    return url
