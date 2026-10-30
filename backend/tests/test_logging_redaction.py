"""Render actual Uvicorn exception logs without exposing request/exception data."""

import asyncio
import io
import json
import logging
from types import SimpleNamespace

import h11
import pytest
import structlog
from uvicorn.protocols.http.flow_control import FlowControl
from uvicorn.protocols.http.h11_impl import RequestResponseCycle

from app.logging.config import configure_logging
from app.main import create_app


@pytest.fixture
def uvicorn_output():
    logger = logging.getLogger("uvicorn.error")
    original = (logger.handlers[:], logger.filters[:], logger.propagate, logger.level)
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers = [handler]
    logger.filters = []
    logger.propagate = False
    logger.setLevel(logging.INFO)
    try:
        yield logger, output
    finally:
        logger.handlers, logger.filters, logger.propagate, logger.level = original
        handler.close()


def test_actual_uvicorn_asgi_failure_keeps_safe_response_and_safe_rendered_log(
    uvicorn_output,
):
    logger, output = uvicorn_output
    configure_logging("INFO")
    application = create_app()

    @application.get("/logging-private/{identifier}")
    async def failure(identifier: str):
        raise RuntimeError("PRIVATE_EXCEPTION_SECRET")

    sent = []

    async def drive():
        connection = h11.Connection(h11.SERVER)
        connection.receive_data(
            b"GET /logging-private/PRIVATE_PATH_SECRET"
            b"?PRIVATE_QUERY_SECRET HTTP/1.1\r\n"
            b"Host: testserver\r\n\r\n"
        )
        connection.next_event()
        connection.next_event()
        transport = SimpleNamespace(
            write=sent.append,
            close=lambda: None,
            is_closing=lambda: False,
        )
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/logging-private/PRIVATE_PATH_SECRET",
            "raw_path": b"/logging-private/PRIVATE_PATH_SECRET",
            "query_string": b"PRIVATE_QUERY_SECRET",
            "root_path": "",
            "headers": [
                (b"host", b"testserver"),
                (b"authorization", b"PRIVATE_AUTH_SECRET"),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
        cycle = RequestResponseCycle(
            scope=scope,
            conn=connection,
            transport=transport,
            flow=FlowControl(transport),
            logger=logger,
            access_logger=logging.getLogger("uvicorn.access"),
            access_log=False,
            default_headers=[],
            message_event=asyncio.Event(),
            on_response=lambda: None,
        )
        await cycle.run_asgi(application)
        assert cycle.response_started and cycle.response_complete

    asyncio.run(drive())
    rendered = output.getvalue()
    assert "PRIVATE_" not in rendered
    assert "Traceback" not in rendered
    event = json.loads(rendered)
    assert event["event"] == "asgi_server_error"
    assert event["error_category"] == "RuntimeError"
    wire = b"".join(sent)
    assert wire.startswith(b"HTTP/1.1 500")
    assert b"internal_error" in wire and b"PRIVATE_" not in wire


@pytest.mark.parametrize("cached", ["exc_text", "stack_info", "both"])
def test_cached_traceback_and_stack_text_cannot_leak_through_formatter(
    uvicorn_output,
    cached,
):
    logger, output = uvicorn_output
    configure_logging("INFO")
    record = logger.makeRecord(
        logger.name,
        logging.ERROR,
        __file__,
        1,
        "PRIVATE_MESSAGE_SECRET %s",
        ("PRIVATE_ARGUMENT_SECRET",),
        None,
    )
    record.message = "PRIVATE_CACHED_MESSAGE_SECRET"
    if cached in {"exc_text", "both"}:
        record.exc_text = "PRIVATE_CACHED_TRACEBACK_SECRET"
    if cached in {"stack_info", "both"}:
        record.stack_info = "PRIVATE_STACK_SECRET"
    logger.handle(record)
    rendered = output.getvalue()
    assert "PRIVATE_" not in rendered
    assert json.loads(rendered)["error_category"] == "unavailable"
    assert record.args == ()
    assert record.exc_info is record.exc_text is record.stack_info is None
    assert "PRIVATE_" not in record.message


def test_repeated_configuration_is_idempotent_and_keeps_safe_server_messages(
    uvicorn_output,
):
    logger, output = uvicorn_output
    configure_logging("INFO")
    filter_count = len(logger.filters)
    configure_logging("WARNING")
    configure_logging("INFO")
    assert filter_count == len(logger.filters) == 1
    logger.info("Safe server startup")
    assert output.getvalue().strip() == "Safe server startup"


def test_structured_application_logs_and_level_are_preserved():
    configure_logging("WARNING")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        logger = structlog.get_logger("synthetic-logging-review")
        logger.info("not_visible")
        logger.warning("safe_application_warning", component="testing")
    finally:
        root.removeHandler(handler)
        handler.close()
    event = json.loads(stream.getvalue())
    assert event["event"] == "safe_application_warning"
    assert event["component"] == "testing"
    assert event["level"] == "warning"
    assert "timestamp" in event


@pytest.mark.parametrize(
    "error,category",
    [
        (
            ExceptionGroup(
                "PRIVATE_GROUP_SECRET", [ValueError("PRIVATE_NESTED_SECRET")]
            ),
            "ExceptionGroup",
        ),
        (type("X" * 100, (Exception,), {})("PRIVATE_EXCEPTION_SECRET"), "unavailable"),
        (
            type("unsafe\ncategory", (Exception,), {})("PRIVATE_EXCEPTION_SECRET"),
            "unavailable",
        ),
    ],
)
def test_exception_groups_and_unsafe_class_names_cannot_leak_rendered_data(
    uvicorn_output,
    error,
    category,
):
    logger, output = uvicorn_output
    configure_logging("INFO")
    logger.error("PRIVATE_MESSAGE_SECRET %s", "PRIVATE_ARGUMENT_SECRET", exc_info=error)
    rendered = output.getvalue()
    assert "PRIVATE_" not in rendered
    assert "Traceback" not in rendered
    assert json.loads(rendered) == {
        "event": "asgi_server_error",
        "error_category": category,
    }
