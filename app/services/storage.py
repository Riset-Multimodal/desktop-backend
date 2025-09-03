from pathlib import Path
from datetime import datetime
import json
from threading import Lock
from app.core.config import settings

_lock = Lock()

def ensure_dirs():
    settings.POSTURE_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

def save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
        f.write("\n")

def update_user_history(email: str, capture_id: str, results: dict) -> None:
    user_dir = settings.POSTURE_DIR / f"{email}_posture"
    user_dir.mkdir(parents=True, exist_ok=True)
    log_path = user_dir / "analysis_history.json"

    with _lock:
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
    with _lock:
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
