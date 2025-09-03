# app/api/v1/endpoints/keylogger.py
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import storage
from app.api.deps import get_db
from app.models import Keylog
from app.services.db_helpers import get_or_create_user

router = APIRouter()

@router.post("/keylogger")
async def receive_keylogger(payload: dict, db: Session = Depends(get_db)):
    if not payload:
        raise HTTPException(status_code=400, detail="Payload kosong")
    email = payload.get("email")
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email diperlukan")

    # simpan JSONL (opsional)
    folder = f"{email}_keylogger"
    log_path = settings.LOGS_DIR / folder / f"log_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    storage.append_jsonl(log_path, payload)

    # === SIMPAN KE DB ===
    get_or_create_user(db, email=email)

    # Map payload → kolom Keylog (gunakan .get dengan default None)
    features = payload.get("features", {})

    row = Keylog(
        user_email=payload.get("email"),
        type=features.get("type"),
        keystroke_count=features.get("keystroke_count"),
        left_click_count=features.get("left_click_count"),
        right_click_count=features.get("right_click_count"),
        scroll_up=features.get("scroll_up"),
        scroll_down=features.get("scroll_down"),
        space_count=features.get("space_count"),
        error_rate=features.get("error_rate"),
        mean_dwell_time_ms=features.get("mean_dwell_time_ms"),
        std_dev_dwell_time_ms=features.get("std_dev_dwell_time_ms"),
        mean_flight_time_ms=features.get("mean_flight_time_ms"),
        std_dev_flight_time_ms=features.get("std_dev_flight_time_ms"),
        mean_digraph_time_ms=features.get("mean_digraph_time_ms"),
        std_dev_digraph_time_ms=features.get("std_dev_digraph_time_ms"),
        pause_count=features.get("pause_count"),
        mean_pause_duration_ms=features.get("mean_pause_duration_ms"),
        mean_burst_length=features.get("mean_burst_length"),
    )

    db.add(row)
    db.commit()
    # ====================

    return {
        "status":"success",
        "data":{
            "saved_to": str(log_path),
            "db": {"keylog_event_id": row.id}
        }
    }
