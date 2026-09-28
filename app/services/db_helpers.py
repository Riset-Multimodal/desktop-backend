# app/services/db_helpers.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User

def get_or_create_user(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.user_email == email))
    if user:
        return user
    # Request paralel (mis. keylogger + posture) bisa sama-sama membuat user baru;
    # pakai savepoint supaya yang kalah cukup membaca ulang, bukan 500.
    try:
        with db.begin_nested():
            user = User(user_email=email)
            db.add(user)
    except IntegrityError:
        user = db.scalar(select(User).where(User.user_email == email))
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
