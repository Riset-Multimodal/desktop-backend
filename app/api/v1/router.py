from fastapi import APIRouter
from .endpoints import posture, keylogger, health, tlx, nordic, user, validation

api_router = APIRouter()
api_router.include_router(posture.router, tags=["posture"])
api_router.include_router(keylogger.router, tags=["keylogger"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tlx.router, tags=["TLX"])
api_router.include_router(nordic.router, tags=["Nordic"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(validation.router, tags=["validation"])