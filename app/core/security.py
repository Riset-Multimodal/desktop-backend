# app/core/security.py
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


class AuthConfigError(RuntimeError):
    pass


def verify_shared_password(password: str) -> bool:
    if not settings.SHARED_PASSWORD_HASH:
        raise AuthConfigError("SHARED_PASSWORD_HASH belum dikonfigurasi")
    try:
        return bcrypt.checkpw(password.encode("utf-8"), settings.SHARED_PASSWORD_HASH.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(email: str) -> tuple[str, datetime]:
    if not settings.JWT_SECRET:
        raise AuthConfigError("JWT_SECRET belum dikonfigurasi")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": email, "exp": expires_at},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, expires_at


def decode_access_token(token: str) -> str | None:
    if not settings.JWT_SECRET:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) and sub else None
