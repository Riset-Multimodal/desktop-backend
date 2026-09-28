import os, re
from app.core.config import settings

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in settings.ALLOWED_EXTENSIONS

def secure_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name).lstrip(".")
    return name or "file"

def safe_path_segment(value: str) -> str:
    """Satu segmen path yang aman dari input user (mis. email): tanpa '/', '\\' atau '..'."""
    seg = re.sub(r"[^A-Za-z0-9@._+-]", "_", value)
    seg = re.sub(r"\.{2,}", "_", seg).strip(".")
    return seg[:200] or "unknown"
