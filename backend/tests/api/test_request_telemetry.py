"""Operational ASGI metadata must neither expose contents nor change responses."""

import asyncio
import json
from dataclasses import asdict
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from starlette.routing import Route

from app.core.request_telemetry import (
    UNMATCHED_ROUTE,
    RequestTelemetryMiddleware,
)
from app.main import create_app


@pytest.fixture
def observed_app(monkeypatch):
    records = []
    # Patch only this module's logger; no global log configuration/state retained.
    from app.core import request_telemetry

    class Logger:
        def info(self, event, **fields):
            records.append((event, fields))

    monkeypatch.setattr(
        request_telemetry,
        "structlog",
        SimpleNamespace(get_logger=lambda *args: Logger()),
    )
    application = create_app()

    @application.get("/telemetry-probe/{identifier}")
    async def probe(identifier: int):
        return {"ok": True}

    @application.post("/telemetry-failure/{identifier}")
    async def failure(identifier: str, request: Request):
        await request.body()
        raise RuntimeError("PRIVATE_EXCEPTION_SECRET")

    @application.get("/telemetry-database-failure")
    async def database_failure():
        raise SQLAlchemyError("PRIVATE_DATABASE_SECRET")

    yield application, records


def request_records(records):
    return [fields for event, fields in records if event == "http_request_finished"]


@pytest.mark.parametrize(
    "method,path,expected_status,template,error",
    [
        ("GET", "/health", 200, "/health", None),
        ("GET", "/api/v1/watchlist", 401, "/api/v1/watchlist", None),
        ("GET", "/PRIVATE_UNMATCHED_SECRET", 404, UNMATCHED_ROUTE, None),
        (
            "GET",
            "/telemetry-database-failure",
            500,
            "/telemetry-database-failure",
            None,
        ),
        (
            "GET",
            "/telemetry-probe/PRIVATE_PATH_SECRET",
            422,
            "/telemetry-probe/{identifier}",
            None,
        ),
        (
            "POST",
            "/telemetry-failure/PRIVATE_PATH_SECRET",
            500,
            "/telemetry-failure/{identifier}",
            "RuntimeError",
        ),
    ],
)
def test_actual_app_status_templates_and_redaction(
    observed_app, method, path, expected_status, template, error
):
    application, records = observed_app
    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.request(
            method,
            path + "?PRIVATE_QUERY_SECRET=secret",
            headers={
                "Authorization": "Bearer PRIVATE_AUTH_SECRET",
                "Cookie": "session=PRIVATE_COOKIE_SECRET",
                "X-Request-ID": "PRIVATE_CALLER_ID_SECRET",
                "X-Owner": "PRIVATE_OWNER_SECRET",
            },
            content="PRIVATE_BODY_SECRET",
        )
    assert response.status_code == expected_status
    events = request_records(records)
    assert len(events) == 1
    event = events[0]
    assert set(event) == {
        "request_id",
        "method",
        "route_template",
        "status",
        "duration_ms",
        "error_category",
    }
    assert str(UUID(event["request_id"])) == event["request_id"]
    assert event["method"] == method
    assert event["route_template"] == template
    assert event["status"] == expected_status
    assert event["error_category"] == error
    assert isinstance(event["duration_ms"], float) and event["duration_ms"] >= 0
    assert "PRIVATE_" not in json.dumps(event)


def test_server_ids_are_unique_and_do_not_reuse_caller_headers(observed_app):
    application, records = observed_app
    with TestClient(application) as client:
        for _ in range(2):
            assert (
                client.get("/health", headers={"X-Request-ID": "caller"}).status_code
                == 200
            )
    assert len({item["request_id"] for item in request_records(records)}) == 2


def test_default_logger_failure_does_not_change_actual_application(monkeypatch):
    from app.core import request_telemetry

    class BrokenLogger:
        def info(self, *args, **kwargs):
            raise RuntimeError("PRIVATE_LOGGER_SECRET")

    monkeypatch.setattr(
        request_telemetry,
        "structlog",
        SimpleNamespace(get_logger=lambda *args: BrokenLogger()),
    )
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def run_asgi(application, scope):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(application(scope, receive, send))
    return messages


def scope(method="GET", route=None):
    value = {
        "type": "http",
        "method": method,
        "path": "/PRIVATE_PATH_SECRET",
        "query_string": b"PRIVATE_QUERY_SECRET",
        "headers": [(b"authorization", b"Bearer PRIVATE_AUTH_SECRET")],
    }
    if route is not None:
        value["route"] = route
    return value


def test_streaming_messages_pass_through_unchanged_once():
    events = []
    original = [
        {"type": "http.response.start", "status": 206, "headers": [(b"x-safe", b"1")]},
        {"type": "http.response.body", "body": b"part-one", "more_body": True},
        {"type": "http.response.body", "body": b"part-two", "more_body": False},
    ]

    async def application(scope, receive, send):
        for message in original:
            await send(message)

    middleware = RequestTelemetryMiddleware(application, sink=events.append)
    assert run_asgi(middleware, scope()) == original
    assert len(events) == 1 and events[0].status == 206
    assert events[0].error_category is None


@pytest.mark.parametrize("response_started", [False, True])
def test_original_error_and_started_status_preserved_even_when_sink_fails(
    response_started,
):
    seen = []
    sent = []
    error = RuntimeError("PRIVATE_ORIGINAL_ERROR")

    async def application(scope, receive, send):
        if response_started:
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send(
                {"type": "http.response.body", "body": b"part", "more_body": True}
            )
        raise error

    def broken_sink(event):
        seen.append(event)
        raise ValueError("PRIVATE_SINK_ERROR")

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        sent.append(message)

    with pytest.raises(RuntimeError) as caught:
        asyncio.run(
            RequestTelemetryMiddleware(application, sink=broken_sink)(
                scope(), receive, send
            )
        )
    assert caught.value is error
    assert len(seen) == 1
    assert seen[0].status == (200 if response_started else 500)
    assert seen[0].error_category == "RuntimeError"
    assert len(sent) == (2 if response_started else 0)


@pytest.mark.parametrize("kind", ["websocket", "lifespan"])
def test_non_http_is_transparent_without_metadata(kind):
    seen = []
    original = {"type": kind, "private": "PRIVATE_NONHTTP_SECRET"}

    async def application(scope, receive, send):
        seen.append(scope)
        await send({"type": "private-pass-through"})

    records = []
    middleware = RequestTelemetryMiddleware(application, sink=records.append)
    assert run_asgi(middleware, original) == [{"type": "private-pass-through"}]
    assert seen == [original] and records == []


@pytest.mark.parametrize("route", [None, object(), {"path": "/PRIVATE_ROUTE_SECRET"}])
def test_untrusted_route_metadata_is_never_logged(route):
    records = []

    async def application(scope, receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    run_asgi(
        RequestTelemetryMiddleware(application, sink=records.append), scope(route=route)
    )
    assert records[0].route_template == UNMATCHED_ROUTE
    assert "PRIVATE_" not in json.dumps(asdict(records[0]))


@pytest.mark.parametrize("path", ["/" + "x" * 300, None, 42])
def test_actual_route_template_length_and_unrecognized_method_are_bounded(path):
    records = []

    async def endpoint(request):
        return None

    route = Route("/safe-template", endpoint)
    route.path = path

    async def application(scope, receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    run_asgi(
        RequestTelemetryMiddleware(application, sink=records.append),
        scope(method="PRIVATE_METHOD_SECRET", route=route),
    )
    assert records[0].method == "OTHER"
    assert records[0].route_template == "<template-unavailable>"


@pytest.mark.parametrize("method", ["PRIVATE_METHOD_SECRET", ["PRIVATE_METHOD_SECRET"]])
def test_unknown_or_malformed_methods_use_fixed_label(method):
    records = []

    async def application(scope, receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    run_asgi(
        RequestTelemetryMiddleware(application, sink=records.append),
        scope(method=method),
    )
    assert records[0].method == "OTHER"
    assert "PRIVATE_" not in json.dumps(asdict(records[0]))


@pytest.mark.parametrize("status", ["PRIVATE_STATUS_SECRET", None, 99, 600, True])
def test_invalid_asgi_status_is_bounded_without_altering_messages(status):
    records = []
    original = [
        {"type": "http.response.start", "status": status, "headers": []},
        {"type": "http.response.body", "body": b""},
    ]

    async def application(scope, receive, send):
        for message in original:
            await send(message)

    assert (
        run_asgi(RequestTelemetryMiddleware(application, sink=records.append), scope())
        == original
    )
    assert len(records) == 1 and records[0].status == 500
    assert records[0].error_category is None


def test_elapsed_time_uses_monotonic_clock(monkeypatch):
    from app.core import request_telemetry

    values = iter([100.0, 100.125])
    monkeypatch.setattr(request_telemetry, "perf_counter", lambda: next(values))
    records = []

    async def application(scope, receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    run_asgi(RequestTelemetryMiddleware(application, sink=records.append), scope())
    assert records[0].duration_ms == 125.0


@pytest.mark.parametrize("response_started", [False, True])
def test_cancellation_passes_through_without_claiming_body_completion(response_started):
    records = []
    messages = []
    cancellation = asyncio.CancelledError()

    async def application(scope, receive, send):
        if response_started:
            await send({"type": "http.response.start", "status": 200, "headers": []})
        raise cancellation

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        messages.append(message)

    with pytest.raises(asyncio.CancelledError) as caught:
        asyncio.run(
            RequestTelemetryMiddleware(application, sink=records.append)(
                scope(), receive, send
            )
        )
    assert caught.value is cancellation
    assert len(records) == 1
    assert records[0].status == (200 if response_started else None)
    assert records[0].error_category is None
    assert len(messages) == (1 if response_started else 0)
