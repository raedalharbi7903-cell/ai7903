from fastapi import APIRouter, FastAPI

from app.api.health import router as health_router
from app.api.v1.router import v1_router

api_router = APIRouter()
api_router.include_router(health_router)


def register_api_routes(app: FastAPI, *, v1_prefix: str) -> None:
    """Register unversioned compatibility routes and versioned API routes."""
    app.include_router(api_router)
    app.include_router(v1_router, prefix=v1_prefix)
