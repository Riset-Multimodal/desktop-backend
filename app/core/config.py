# app/core/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ergonomics & Keylogger API"
    VERSION: str = "1.0.0"

    # Upload limits
    MAX_REQUEST_BYTES: int = 16 * 1024 * 1024
    MAX_IMAGE_BYTES: int = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}

    # Storage (lokal)
    STORAGE_ROOT: Path = BASE_DIR / "data"
    POSTURE_DIR: Path = STORAGE_ROOT / "uploads" / "posture"
    LOGS_DIR: Path = STORAGE_ROOT / "logs"
    # analysis_history.json & global_average.json (pipeline lama). Default mati:
    # datanya sudah ada di DB dan file ini ditulis ulang utuh setiap capture.
    LEGACY_FILE_LOGS: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./ergokey.db"  # override via .env

    # Auth
    # Secret untuk tanda tangan JWT. WAJIB diisi di .env production.
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 24 * 60
    # bcrypt hash dari password bersama peserta (dulu di-hardcode di desktop-app)
    SHARED_PASSWORD_HASH: Optional[str] = None
    # API key untuk akses admin (list semua user/response). Kirim via header X-API-Key.
    ADMIN_API_KEY: Optional[str] = None

    # CORS (auth pakai Bearer token, bukan cookie, jadi credentials tidak dipakai)
    CORS_ORIGINS: list[str] = ["*"]

    # Supabase (opsional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: Optional[str] = None
    SUPABASE_SIGNED_URL_TTL: int = 60 * 60

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",          # baca dari .env
        env_file_encoding="utf-8",
        extra="ignore",           # abaikan env diluar field yg didefinisikan
    )

settings = Settings()
