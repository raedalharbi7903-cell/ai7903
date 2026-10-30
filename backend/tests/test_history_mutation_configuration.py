"""Explicit origin and separate audit-retention configuration validation."""

import pytest

from app.config.settings import Settings


@pytest.mark.parametrize(
    "origin",
    [
        "https://frontend.test/path",
        "https://frontend.test?query=1",
        "https://frontend.test#fragment",
        "https://user:secret@frontend.test",
        "https://*.frontend.test",
        "http://frontend.test",
        "null",
    ],
)
def test_invalid_mutation_origins_fail_configuration(origin):
    with pytest.raises(ValueError):
        Settings(
            _env_file=None, APP_ENVIRONMENT="testing", HISTORY_ALLOWED_ORIGIN=origin
        )


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_real_environments_require_https_even_for_loopback(environment):
    with pytest.raises(ValueError):
        Settings(
            _env_file=None,
            APP_ENVIRONMENT=environment,
            HISTORY_ALLOWED_ORIGIN="http://127.0.0.1:5173",
        )


@pytest.mark.parametrize(
    "origin",
    [
        "https://frontend.test",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://[::1]:5173",
    ],
)
def test_explicit_safe_testing_origins_have_no_path_or_credentials(origin):
    settings = Settings(
        _env_file=None, APP_ENVIRONMENT="testing", HISTORY_ALLOWED_ORIGIN=origin
    )
    assert str(settings.history_allowed_origin).rstrip("/") == origin


def test_write_audit_policy_has_no_default_duration_or_origin(monkeypatch):
    for name in (
        "HISTORY_MUTATIONS_ENABLED",
        "HISTORY_AUDIT_RETENTION_SECONDS",
        "HISTORY_AUDIT_POLICY_REFERENCE",
        "HISTORY_ALLOWED_ORIGIN",
    ):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(_env_file=None)
    assert settings.history_mutations_enabled is False
    assert settings.history_audit_retention_seconds is None
    assert settings.history_audit_policy_reference is None
    assert settings.history_allowed_origin is None
