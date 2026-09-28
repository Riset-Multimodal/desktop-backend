# app/api/v1/endpoints/health.py
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db

logger = logging.getLogger("ergokey")
router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint untuk mengecek status aplikasi dan database.
    - Jika API dan DB sehat -> return status 200
    - Jika DB gagal -> return status 503 (detail error hanya di log server)
    """
    try:
        # Tes koneksi database
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "message": "API dan database berjalan normal."
        }
    except Exception:
        logger.exception("Health check: database error")
        return JSONResponse(status_code=503, content={
            "status": "unhealthy",
            "database": "disconnected",
            "message": "Database tidak dapat dihubungi."
        })
