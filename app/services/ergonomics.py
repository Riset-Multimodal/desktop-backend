from threading import Lock
from typing import Optional, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger("ergokey")

try:
    from app.services.PostureAnalyze.func_main import analyze_ergonomics_from_files
except ImportError:
    logger.exception("Modul PostureAnalyze gagal di-import; analisis postur tidak tersedia")
    analyze_ergonomics_from_files = None

# Detector MediaPipe di PostureAnalyze adalah objek global dan tidak thread-safe.
# Endpoint sekarang jalan di threadpool, jadi analisis diserialkan per proses
# (paralelisme tetap didapat dari jumlah worker uvicorn).
_analyze_lock = Lock()

def analyze(front: bytes, side: bytes, overhead: bytes) -> Optional[Dict[str, Any]]:
    if analyze_ergonomics_from_files is None:
        return None
    with _analyze_lock:
        return analyze_ergonomics_from_files(
            file_front=front, file_side=side, file_overhead=overhead, save_log=settings.LEGACY_FILE_LOGS
        )
