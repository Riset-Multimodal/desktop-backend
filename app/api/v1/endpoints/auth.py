# app/api/v1/endpoints/auth.py
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import AuthConfigError, create_access_token, verify_shared_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenOut

router = APIRouter()

# Rate limit sederhana per IP (in-memory, per worker) untuk menahan brute force.
_MAX_FAILURES = 10
_WINDOW_SECONDS = 15 * 60
_failures: dict[str, deque] = defaultdict(deque)
_failures_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _too_many_failures(ip: str) -> bool:
    now = time.monotonic()
    with _failures_lock:
        q = _failures[ip]
        while q and now - q[0] > _WINDOW_SECONDS:
            q.popleft()
        return len(q) >= _MAX_FAILURES


def _record_failure(ip: str) -> None:
    with _failures_lock:
        _failures[ip].append(time.monotonic())


@router.post("/auth/login", response_model=TokenOut, summary="Login peserta, mengembalikan access token")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    if _too_many_failures(ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Terlalu banyak percobaan login, coba lagi nanti")

    try:
        password_ok = verify_shared_password(payload.password)
    except AuthConfigError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Login belum dikonfigurasi di server")

    user = db.scalar(select(User).where(func.lower(User.user_email) == str(payload.email).lower()))

    # Pesan dibuat sama supaya tidak bisa dipakai untuk menebak email yang terdaftar.
    if not user or not password_ok:
        _record_failure(ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email atau password salah")

    try:
        token, expires_at = create_access_token(user.user_email)
    except AuthConfigError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Login belum dikonfigurasi di server")

    return TokenOut(access_token=token, expires_at=expires_at, user_email=user.user_email, name=user.name)
