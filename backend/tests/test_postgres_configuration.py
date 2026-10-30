"""PostgreSQL configuration/guard checks, explicitly not server acceptance."""

import pytest
from sqlalchemy import create_engine

from app.config.settings import Settings
from integration.test_postgres import owned_test_url


def test_postgresql_driver_dialect_import_does_not_connect() -> None:
    engine = create_engine("postgresql+psycopg://")
    assert engine.dialect.driver == "psycopg"
    assert engine.dialect.name == "postgresql"
    engine.dispose()


@pytest.mark.parametrize(
    "environment", ["development", "testing", "staging", "production"]
)
def test_four_explicit_environment_names(environment) -> None:
    settings = Settings(_env_file=None, APP_ENVIRONMENT=environment)
    assert settings.environment == environment


@pytest.mark.parametrize(
    "changes",
    [
        {"APP_ENVIRONMENT": "production"},
        {"APP_ENVIRONMENT": "staging"},
        {"POSTGRES_ACCEPTANCE_OWNED_CONTAINER": "not-owned"},
        {"DATABASE_URL": "sqlite://"},
        {
            "DATABASE_URL": "postgresql+psycopg://ci_owner:synthetic@other-host:12345/ai_ci_"
            + "a" * 16
        },
        {
            "DATABASE_URL": "postgresql+psycopg://ci_owner:synthetic@127.0.0.1:12345/customer_production"
        },
        {
            "DATABASE_URL": "postgresql+psycopg://ci_owner@127.0.0.1:12345/ai_ci_"
            + "a" * 16
        },
    ],
)
def test_acceptance_guard_refuses_non_owned_database_without_connecting(
    monkeypatch,
    changes,
) -> None:
    values = {
        "APP_ENVIRONMENT": "testing",
        "POSTGRES_ACCEPTANCE_OWNED_CONTAINER": "b" * 64,
        "DATABASE_URL": (
            "postgresql+psycopg://ci_owner:synthetic@127.0.0.1:12345/ai_ci_" + "a" * 16
        ),
    } | changes
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError, match="Refusing"):
        owned_test_url()
