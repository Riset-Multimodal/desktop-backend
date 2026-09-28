# app/api/deps.py
import secrets
from dataclasses import dataclass
from typing import Generator, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_bearer = HTTPBearer(auto_error=False)
_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass(frozen=True)
class Principal:
    email: Optional[str] = None
    is_admin: bool = False


def _is_admin_key(key: Optional[str]) -> bool:
    return bool(key and settings.ADMIN_API_KEY and secrets.compare_digest(key, settings.ADMIN_API_KEY))


def get_principal(
    creds: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
    api_key: Optional[str] = Security(_api_key),
) -> Principal:
    """User login (Bearer token) atau admin (X-API-Key)."""
    if _is_admin_key(api_key):
        return Principal(is_admin=True)
    if creds and creds.scheme.lower() == "bearer":
        email = decode_access_token(creds.credentials)
        if email:
            return Principal(email=email)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak terautentikasi",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_email(principal: Principal = Depends(get_principal)) -> str:
    """Hanya untuk endpoint milik user yang login (bukan admin key)."""
    if not principal.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Butuh token user")
    return principal.email


def require_admin(principal: Principal = Depends(get_principal)) -> Principal:
    if not principal.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Khusus admin")
    return principal


def ensure_same_email(token_email: str, payload_email: Optional[str]) -> str:
    """Email di body (kalau ada) harus sama dengan pemilik token."""
    if payload_email is not None and str(payload_email).lower() != token_email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email tidak sesuai dengan sesi login")
    return token_email


def scope_email(principal: Principal, requested: Optional[str]) -> Optional[str]:
    """Filter email untuk endpoint list: user biasa selalu dibatasi ke datanya sendiri."""
    if principal.is_admin:
        return requested
    return ensure_same_email(principal.email, requested)
