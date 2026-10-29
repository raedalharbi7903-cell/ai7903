import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.error_handlers import register_exception_handlers


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (RuntimeError("private-token"), "internal_error"),
        (SQLAlchemyError("private-db-url"), "database_error"),
    ],
)
def test_unexpected_errors_have_safe_consistent_json(error, code) -> None:
    application = FastAPI()
    register_exception_handlers(application)

    @application.get("/failure")
    def failure():
        raise error

    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/failure")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == code
    assert "private-" not in response.text
    assert "traceback" not in response.text.lower()
