from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import json
from threading import Lock
from app.core.config import settings
from app.utils.files import safe_path_segment

try:  # lock lintas proses (uvicorn --workers N); tidak tersedia di Windows
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

_lock = Lock()

@contextmanager
def _file_lock(path: Path):
    with _lock:
        if fcntl is None:
            yield
            return
        lock_path = path.with_name(path.name + ".lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

def ensure_dirs():
    settings.POSTURE_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

def user_posture_dir(email: str) -> Path:
    return settings.POSTURE_DIR / f"{safe_path_segment(email)}_posture"

def save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def update_user_history(email: str, capture_id: str, results: dict) -> None:
    user_dir = user_posture_dir(email)
    user_dir.mkdir(parents=True, exist_ok=True)
    log_path = user_dir / "analysis_history.json"

    with _file_lock(log_path):
        hist = {}
        if log_path.exists():
            try:
                hist = json.loads(log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                hist = {}
        hist[capture_id] = {"timestamp": datetime.now().isoformat(), "results": results}
        log_path.write_text(json.dumps(hist, indent=4, ensure_ascii=False), encoding="utf-8")

def update_global_average(results: dict) -> None:
    score = results.get("final_scores_final_rosa_score")
    if score is None:
        return
    path = settings.POSTURE_DIR.parent / "global_average.json"
    with _file_lock(path):
        data = {"total_analyses": 0, "average_rosa_score": 0.0}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        n, avg = int(data["total_analyses"]), float(data["average_rosa_score"])
        new_avg = ((avg * n) + float(score)) / (n + 1)
        data["total_analyses"], data["average_rosa_score"] = n + 1, round(new_avg, 2)
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
