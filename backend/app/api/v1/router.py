from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.v1.analysis import router as analysis_router

v1_router = APIRouter()
v1_router.include_router(health_router)
v1_router.include_router(analysis_router)
