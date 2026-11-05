"""Startup diagnostics preserve categories without printing environment secrets."""

import os
import subprocess
import sys
import traceback

import pytest
from pydantic import ValidationError

from app.config.settings import Settings


@pytest.mark.parametrize(
    "field,value,diagnostic",
    [
        ("LOG_LEVEL", "PRIVATE_LOG_LEVEL_SECRET", "LOG_LEVEL"),
        ("APP_ENVIRONMENT", "PRIVATE_ENVIRONMENT_SECRET", "APP_ENVIRONMENT"),
        (
            "HISTORY_ALLOWED_ORIGIN",
            "PRIVATE_INVALID_ORIGIN_SECRET",
            "HISTORY_ALLOWED_ORIGIN",
        ),
        (
            "HISTORY_ALLOWED_ORIGIN",
            "https://user:PRIVATE_ORIGIN_PASSWORD_SECRET@frontend.test",
            "History origin",
        ),
        (
            "WATCHLIST_ALLOWED_ORIGIN",
            "https://frontend.test?PRIVATE_ORIGIN_QUERY_SECRET",
            "Watchlist origin",
        ),
    ],
)
def test_environment_validation_exception_rendering_redacts_inputs(
    monkeypatch, field, value, diagnostic
):
    monkeypatch.setenv("APP_ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:PRIVATE_DATABASE_PASSWORD_SECRET@db.invalid/ai",
    )
    monkeypatch.setenv("MARKET_DATA_API_KEY", "PRIVATE_UNRELATED_API_KEY_SECRET")
    monkeypatch.setenv(field, value)
    with pytest.raises(ValidationError) as caught:
        Settings(_env_file=None)
    error = caught.value
    assert diagnostic in str(error)
    assert "PRIVATE_" not in str(error)
    assert "PRIVATE_" not in repr(error)
    rendered = "".join(traceback.format_exception_only(type(error), error))
    assert "ValidationError" in rendered
    assert "PRIVATE_" not in rendered
    # Programmatic error inspection must opt out of raw input/context explicitly.
    safe_errors = error.errors(include_input=False, include_context=False)
    assert safe_errors
    assert all("type" in entry and "loc" in entry for entry in safe_errors)
    assert all("input" not in entry and "ctx" not in entry for entry in safe_errors)


def test_real_application_import_failure_does_not_print_environment_values():
    environment = dict(os.environ)
    environment.update(
        APP_NAME="synthetic-startup-redaction",
        APP_ENVIRONMENT="testing",
        LOG_LEVEL="PRIVATE_STARTUP_SECRET",
        DATABASE_URL="postgresql://user:PRIVATE_DB_PASSWORD@db.invalid/ai",
        MARKET_DATA_API_KEY="PRIVATE_UNRELATED_API_KEY_SECRET",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONIOENCODING="utf-8",
    )
    process = subprocess.run(
        [sys.executable, "-c", "from app.main import app"],
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert process.returncode != 0
    assert "ValidationError" in process.stderr
    assert "LOG_LEVEL" in process.stderr
    assert "literal_error" in process.stderr
    assert "PRIVATE_" not in process.stdout + process.stderr


def test_valid_configuration_and_validation_details_are_unchanged(monkeypatch):
    monkeypatch.setenv("APP_NAME", "synthetic-valid-configuration")
    monkeypatch.setenv("APP_ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("HISTORY_ALLOWED_ORIGIN", "https://frontend.test")
    monkeypatch.setenv("WATCHLIST_ALLOWED_ORIGIN", "http://127.0.0.1:5173")
    configuration = Settings(_env_file=None)
    assert configuration.app_name == "synthetic-valid-configuration"
    assert configuration.environment == "testing"
    assert configuration.log_level == "WARNING"
    assert configuration.database_url == "sqlite://"
    assert str(configuration.history_allowed_origin) == "https://frontend.test/"
    assert str(configuration.watchlist_allowed_origin) == "http://127.0.0.1:5173/"
