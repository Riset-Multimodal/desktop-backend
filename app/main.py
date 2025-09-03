from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router

logger = setup_logging()

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

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

@app.on_event("startup")
async def _print_routes_on_worker():
    logger.info("=== EFFECTIVE ROUTES (worker) ===")
    for r in app.router.routes:
        try:
            logger.info("ROUTE: %s %s", ",".join(sorted(r.methods or [])), r.path)
        except Exception:
            pass
