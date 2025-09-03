from fastapi import APIRouter
from .endpoints import posture, keylogger, health

api_router = APIRouter()
api_router.include_router(posture.router, tags=["posture"])
api_router.include_router(keylogger.router, tags=["keylogger"])
api_router.include_router(health.router, tags=["health"])