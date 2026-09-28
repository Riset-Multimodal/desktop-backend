# app/api/v1/endpoints/keylogger.py
from typing import Any, Optional

from fastapi import APIRouter, Depends
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import storage
from app.api.deps import get_db, get_current_email, ensure_same_email
from app.models import Keylog
from app.services.db_helpers import get_or_create_user
from app.utils.files import safe_path_segment

router = APIRouter()

_FEATURE_COLUMNS = (
    "type", "keystroke_count", "left_click_count", "right_click_count", "scroll_up", "scroll_down",
    "space_count", "error_rate", "mean_dwell_time_ms", "std_dev_dwell_time_ms", "mean_flight_time_ms",
    "std_dev_flight_time_ms", "mean_digraph_time_ms", "std_dev_digraph_time_ms", "pause_count",
    "mean_pause_duration_ms", "mean_burst_length", "words_per_minute", "typing_rhythm_consistency",
    "mouse_speed", "mouse_accuracy", "mouse_jerkiness", "raw_x_sequence", "raw_y_sequence",
)


class KeyloggerPayload(BaseModel):
    email: Optional[str] = None
    features: dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


# `def` (bukan async) supaya query DB & tulis file yang blocking jalan di threadpool,
# tidak menahan event loop.
@router.post("/keylogger")
def receive_keylogger(
    payload: KeyloggerPayload,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_email),
):
    ensure_same_email(email, payload.email)
    record = payload.model_dump()
    record["email"] = email

    # simpan JSONL (opsional)
    folder = f"{safe_path_segment(email)}_keylogger"
    log_path = settings.LOGS_DIR / folder / f"log_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    storage.append_jsonl(log_path, record)

    # === SIMPAN KE DB ===
    get_or_create_user(db, email=email)

    features = payload.features
    row = Keylog(user_email=email, **{col: features.get(col) for col in _FEATURE_COLUMNS})

    db.add(row)
    db.commit()
    # ====================

    return {
        "status":"success",
        "data":{
            "saved_to": str(log_path.relative_to(settings.STORAGE_ROOT)),
            "db": {"keylog_event_id": row.id}
        }
    }
