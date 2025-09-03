from typing import Optional, Dict, Any
# jika ingin pindah fungsinya ke sini:
import logging

logger = logging.getLogger("ergokey")

try:
    from app.services.PostureAnalyze.func_main import analyze_ergonomics_from_files
except ImportError:
    analyze_ergonomics_from_files = None

def analyze(front: bytes, side: bytes, overhead: bytes) -> Optional[Dict[str, Any]]:
    if analyze_ergonomics_from_files is None:
        return None
    return analyze_ergonomics_from_files(
        file_front=front, file_side=side, file_overhead=overhead, save_log=True
    )
