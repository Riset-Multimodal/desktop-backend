from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging

from app.api.v1.router import api_router

logger = setup_logging()

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# Auth pakai header Authorization (Bearer), bukan cookie, jadi credentials tidak perlu.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"],
)

if not settings.JWT_SECRET or not settings.SHARED_PASSWORD_HASH:
    logger.warning("JWT_SECRET / SHARED_PASSWORD_HASH belum diset: /auth/login akan menolak semua login")
if not settings.ADMIN_API_KEY:
    logger.warning("ADMIN_API_KEY belum diset: endpoint admin (mis. GET /users) tidak bisa diakses")

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    cl = request.headers.get("content-length")
    try:
        if cl is not None and int(cl) > settings.MAX_REQUEST_BYTES:
            return JSONResponse(status_code=413, content={"status":"error","message":"Request terlalu besar"})
    except ValueError:
        pass
    return await call_next(request)

app.include_router(api_router)

@app.get("/")
def root():
    return {"ok": True, "message": "backend-user up"}