# app/core/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict  # ← ganti ini
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ergonomics & Keylogger API"
    VERSION: str = "1.0.0"

    # Upload limits
    MAX_REQUEST_BYTES: int = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}

    # Storage (lokal)
    STORAGE_ROOT: Path = BASE_DIR / "data"
    POSTURE_DIR: Path = STORAGE_ROOT / "uploads" / "posture"
    LOGS_DIR: Path = STORAGE_ROOT / "logs"

    # Database
    DATABASE_URL: str = "sqlite:///./ergokey.db"  # override via .env

    # Supabase (opsional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: Optional[str] = None

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",          # baca dari .env
        env_file_encoding="utf-8",
        extra="ignore",           # abaikan env diluar field yg didefinisikan
    )

settings = Settings()
