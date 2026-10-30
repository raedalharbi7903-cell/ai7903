import json
import logging
import re

import structlog

MAX_ERROR_CATEGORY_LENGTH = 64


class UvicornExceptionRedaction(logging.Filter):
    """Keep operational category, never native ASGI traceback or exception text.

    Uvicorn re-logs exceptions rethrown by Starlette even after the safe JSON
    response handler has run. Its logger's own handlers bypass root formatting,
    so filtering at uvicorn.error is necessary, not only a root formatter.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not (record.exc_info or record.exc_text or record.stack_info):
            return True
        category = "unavailable"
        if (
            isinstance(record.exc_info, tuple)
            and len(record.exc_info) > 1
            and isinstance(record.exc_info[1], BaseException)
        ):
            name = type(record.exc_info[1]).__name__
            if len(name) <= MAX_ERROR_CATEGORY_LENGTH and re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*", name
            ):
                category = name
        record.msg = json.dumps(
            {"event": "asgi_server_error", "error_category": category}
        )
        record.args = ()
        record.message = record.msg
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        return True


def configure_logging(log_level: str) -> None:
    """Configure JSON structured logs."""
    numeric_log_level = getattr(logging, log_level.upper())
    logging.basicConfig(format="%(message)s", level=numeric_log_level, force=True)
    server_logger = logging.getLogger("uvicorn.error")
    if not any(
        isinstance(item, UvicornExceptionRedaction) for item in server_logger.filters
    ):
        server_logger.addFilter(UvicornExceptionRedaction())
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(numeric_log_level),
        cache_logger_on_first_use=True,
    )
