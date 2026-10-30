"""Bounded HTTP operational metadata, never customer request contents.

Standard FastAPI middleware sits inside ServerErrorMiddleware: when an unhandled
exception escapes before response start, status 500 reflects the application's
registered error handler. After response start the actual sent status is retained.
This is not proof that a streamed body completed or reached the client.
Cancellation before response start has unknown status (None), not a fabricated
server failure. Cancellation after headers retains the actual started status.
"""

from asyncio import CancelledError
from collections.abc import Callable
from dataclasses import asdict, dataclass
from time import perf_counter
from uuid import uuid4

import structlog
from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

HTTP_METHODS = frozenset(
    {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"}
)
UNMATCHED_ROUTE = "<unmatched>"
MAX_ROUTE_TEMPLATE_LENGTH = 256
MAX_ERROR_CATEGORY_LENGTH = 64


@dataclass(frozen=True)
class RequestTelemetry:
    request_id: str
    method: str
    route_template: str
    status: int | None
    duration_ms: float
    error_category: str | None


def log_request(event: RequestTelemetry) -> None:
    structlog.get_logger(__name__).info("http_request_finished", **asdict(event))


def route_template(scope: Scope) -> str:
    route = scope.get("route")
    if not isinstance(route, Route):
        return UNMATCHED_ROUTE
    template = route.path
    if not isinstance(template, str) or len(template) > MAX_ROUTE_TEMPLATE_LENGTH:
        return "<template-unavailable>"
    return template


class RequestTelemetryMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        sink: Callable[[RequestTelemetry], None] = log_request,
    ) -> None:
        self.app = app
        self._sink = sink

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = str(uuid4())
        started = perf_counter()
        response_status: int | None = None
        error_category: str | None = None
        cancelled = False

        async def observed_send(message: Message) -> None:
            nonlocal response_status
            await send(message)
            if message["type"] == "http.response.start" and response_status is None:
                status = message.get("status")
                if type(status) is int and 100 <= status <= 599:
                    response_status = status

        try:
            await self.app(scope, receive, observed_send)
        except CancelledError:
            cancelled = True
            raise
        except Exception as error:
            error_category = type(error).__name__[:MAX_ERROR_CATEGORY_LENGTH]
            if response_status is None:
                response_status = 500
            raise
        finally:
            try:
                method = scope.get("method")
                self._sink(
                    RequestTelemetry(
                        request_id=request_id,
                        method=(
                            method
                            if isinstance(method, str) and method in HTTP_METHODS
                            else "OTHER"
                        ),
                        route_template=route_template(scope),
                        status=(
                            response_status
                            if response_status is not None or cancelled
                            else 500
                        ),
                        duration_ms=round(max(0.0, perf_counter() - started) * 1000, 3),
                        error_category=error_category,
                    )
                )
            except Exception:
                # Operational logging must never alter/replace a response or
                # mask the original application/transport exception.
                pass
