# app/services/db_helpers.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User

def get_or_create_user(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.user_email == email))
    if not user:
        user = User(user_email=email)
        db.add(user)
        db.flush()
    return user

# OPTIONAL: casting ringan untuk numeric/bool jika perlu
def coerce_results_for_posture(results: dict) -> dict:
    if not isinstance(results, dict):
        return {}
    out = {}
    for k, v in results.items():
        if v in ("", None):
            out[k] = None
            continue
        # contoh kecil: convert "true"/"false"
        if isinstance(v, str) and v.lower() in ("true", "false"):
            out[k] = v.lower() == "true"
        else:
            out[k] = v
    return out
