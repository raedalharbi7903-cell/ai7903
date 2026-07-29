from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.router import api_router
from app.config.settings import get_settings
from app.core.error_handlers import register_exception_handlers
from app.logging.config import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = structlog.get_logger(__name__)
    logger.info("application_started", environment=settings.environment)
    yield
    logger.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.include_router(api_router)
    register_exception_handlers(application)
    return application


app = create_app()
