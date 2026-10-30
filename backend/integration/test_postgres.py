"""Actual PostgreSQL acceptance; explicitly run only by the owned-server harness."""

import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import make_url, text
from sqlalchemy.exc import IntegrityError

from app.config.settings import get_settings
from app.database.session import get_db_session, get_engine, get_session_factory


def owned_test_url() -> None:
    url = make_url(os.environ.get("DATABASE_URL", "sqlite://"))
    if (
        os.environ.get("APP_ENVIRONMENT") != "testing"
        or not re.fullmatch(
            r"[0-9a-f]{64}", os.environ.get("POSTGRES_ACCEPTANCE_OWNED_CONTAINER", "")
        )
        or url.drivername != "postgresql+psycopg"
        or url.host != "127.0.0.1"
        or not url.port
        or url.username != "ci_owner"
        or not url.password
        or not re.fullmatch(r"ai_ci_[0-9a-f]{16}", url.database or "")
    ):
        raise RuntimeError("Refusing PostgreSQL acceptance outside owned test server")


def migrate(*arguments: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, "Owned PostgreSQL migration command failed"
    return result.stdout


@pytest.fixture(scope="module", autouse=True)
def owned_database():
    owned_test_url()
    get_settings.cache_clear()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
    migrate("upgrade", "head")
    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE acceptance_probe "
                "(id integer PRIMARY KEY, value integer NOT NULL CHECK (value > 0))"
            )
        )
    yield engine
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE acceptance_probe"))
    engine.dispose()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
    get_settings.cache_clear()


def test_actual_psycopg_connection_and_migration_roundtrip(owned_database):
    assert owned_database.dialect.driver == "psycopg"
    with owned_database.connect() as connection:
        assert connection.scalar(text("SELECT current_database()")).startswith("ai_ci_")
        assert "PostgreSQL 17." in connection.scalar(text("SELECT version()"))
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "20260725_0001"
        )
    migrate("downgrade", "base")
    migrate("upgrade", "head")
    assert "20260725_0001" in migrate("current")


def test_session_close_has_no_hidden_commit(owned_database):
    provider = get_db_session()
    session = next(provider)
    session.execute(text("INSERT INTO acceptance_probe VALUES (1, 1)"))
    provider.close()
    with owned_database.connect() as connection:
        assert (
            connection.scalar(text("SELECT count(*) FROM acceptance_probe WHERE id=1"))
            == 0
        )


def test_failed_request_rolls_back_real_transaction(owned_database):
    provider = get_db_session()
    session = next(provider)
    session.execute(text("INSERT INTO acceptance_probe VALUES (2, 1)"))
    with pytest.raises(RuntimeError, match="synthetic-request-failure"):
        provider.throw(RuntimeError("synthetic-request-failure"))
    with owned_database.connect() as connection:
        assert (
            connection.scalar(text("SELECT count(*) FROM acceptance_probe WHERE id=2"))
            == 0
        )


def test_constraints_and_parameter_binding(owned_database):
    with pytest.raises(IntegrityError):
        with owned_database.begin() as connection:
            connection.execute(text("INSERT INTO acceptance_probe VALUES (3, -1)"))
    with owned_database.begin() as connection:
        connection.execute(
            text("INSERT INTO acceptance_probe VALUES (:id, :value)"),
            {"id": 3, "value": 7},
        )
        value = "نص تجريبي ' ; DROP TABLE acceptance_probe; --"
        assert (
            connection.scalar(text("SELECT CAST(:value AS text)"), {"value": value})
            == value
        )
    with owned_database.connect() as connection:
        assert (
            connection.scalar(text("SELECT value FROM acceptance_probe WHERE id=3"))
            == 7
        )


def test_no_dirty_reads_and_explicit_commit(owned_database):
    with get_session_factory()() as writer:
        writer.execute(text("INSERT INTO acceptance_probe VALUES (4, 1)"))
        with owned_database.connect() as reader:
            assert (
                reader.scalar(text("SELECT count(*) FROM acceptance_probe WHERE id=4"))
                == 0
            )
        writer.commit()
        with owned_database.connect() as reader:
            assert (
                reader.scalar(text("SELECT count(*) FROM acceptance_probe WHERE id=4"))
                == 1
            )


def test_concurrent_atomic_updates_do_not_lose_committed_values(owned_database):
    with owned_database.begin() as connection:
        connection.execute(text("INSERT INTO acceptance_probe VALUES (5, 1)"))

    def increment(_):
        with get_session_factory()() as session:
            session.execute(text("SET LOCAL statement_timeout = '5s'"))
            session.execute(
                text("UPDATE acceptance_probe SET value=value+1 WHERE id=5")
            )
            session.commit()

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(increment, range(32)))
    with owned_database.connect() as connection:
        assert (
            connection.scalar(text("SELECT value FROM acceptance_probe WHERE id=5"))
            == 33
        )
