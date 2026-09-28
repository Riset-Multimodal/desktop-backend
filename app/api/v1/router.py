from fastapi import APIRouter
from .endpoints import posture, keylogger, health, tlx, nordic, user, validation, auth, questionnaire

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(posture.router, tags=["posture"])
api_router.include_router(keylogger.router, tags=["keylogger"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tlx.router, tags=["TLX"])
api_router.include_router(nordic.router, tags=["Nordic"])
api_router.include_router(questionnaire.router, tags=["questionnaire"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(validation.router, tags=["validation"])
