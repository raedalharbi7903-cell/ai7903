"""Actual PostgreSQL acceptance; explicitly run only by the owned-server harness."""

import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl
from sqlalchemy import func, make_url, select, text
from sqlalchemy.exc import IntegrityError

from app.analysis.models import AnalysisResult
from app.config.settings import get_settings
from app.database.session import get_db_session, get_engine, get_session_factory
from app.main import create_app
from app.models.analysis_history import AnalysisHistoryRecord
from app.models.audit import AuditEvent
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.security.dependencies import get_session_verifier
from app.security.identity import VerifiedSession, principal_key
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy
from app.services.history_mutations import AuditPolicy, HistoryMutationService
from tests.analysis.test_pipeline import fixture_input
from tests.api.test_analysis import payload as api_payload


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
            "20261030_0003"
        )
    migrate("downgrade", "base")
    migrate("upgrade", "head")
    assert "20261030_0003" in migrate("current")


def test_audit_upgrade_preserves_previous_history_on_actual_postgres(owned_database):
    migrate("downgrade", "20261030_0002")
    identity = VerifiedSession(
        issuer="synthetic-migration",
        subject="history-probe",
        email_verified=True,
        mfa_verified=False,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    try:
        with get_session_factory()() as session:
            history = AnalysisHistoryService(
                AnalysisHistoryRepository(session),
                policy=HistoryPolicy(
                    retention_seconds=3600,
                    approval_reference="synthetic-migration-only",
                ),
            )
            entry = history.analyze_and_record(identity, fixture_input())
            session.commit()
    finally:
        migrate("upgrade", "head")
    with get_session_factory()() as session:
        history = AnalysisHistoryService(
            AnalysisHistoryRepository(session),
            policy=HistoryPolicy(
                retention_seconds=3600, approval_reference="synthetic-migration-only"
            ),
        )
        assert (
            history.get(identity, entry.id).result.model_dump()
            == entry.result.model_dump()
        )


def test_history_owner_isolation_and_pipeline_snapshot_on_postgres(owned_database):
    now = datetime.now(UTC)
    alice = VerifiedSession(
        issuer="synthetic-pg",
        subject="alice",
        email_verified=True,
        mfa_verified=False,
        expires_at=now + timedelta(hours=1),
    )
    bob = alice.model_copy(update={"subject": "bob"})
    with get_session_factory()() as session:
        history = AnalysisHistoryService(
            AnalysisHistoryRepository(session),
            policy=HistoryPolicy(
                retention_seconds=60, approval_reference="synthetic-pg-policy-only"
            ),
            clock=lambda: now,
        )
        entry = history.analyze_and_record(alice, fixture_input())
        session.commit()
        session.expire_all()
        saved = history.get(alice, entry.id)
        assert saved is not None
        assert len(saved.result.outputs) == 28
        assert saved.result.model_dump() == entry.result.model_dump()
        assert saved.created_at == now
        assert history.get(bob, entry.id) is None
        assert history.list(bob) == []
        assert history.delete(bob, entry.id) is False
        assert history.get(alice, entry.id) is not None


def test_history_bounded_expiry_purge_on_postgres(owned_database):
    clock = [datetime.now(UTC)]
    alice = VerifiedSession(
        issuer="synthetic-expiry",
        subject="alice",
        email_verified=True,
        mfa_verified=False,
        expires_at=clock[0] + timedelta(hours=1),
    )
    bob = alice.model_copy(update={"subject": "bob"})
    with get_session_factory()() as session:
        history = AnalysisHistoryService(
            AnalysisHistoryRepository(session),
            policy=HistoryPolicy(
                retention_seconds=5, approval_reference="synthetic-expiry-only"
            ),
            clock=lambda: clock[0],
        )
        for _ in range(3):
            history.record(alice, AnalysisResult(status="completed"))
        foreign = history.record(bob, AnalysisResult(status="completed"))
        session.commit()
        clock[0] += timedelta(seconds=5)
        assert history.list(alice) == []
        assert history.purge_expired(alice, limit=2) == 2
        assert history.purge_expired(alice, limit=2) == 1
        assert history.purge_expired(alice, limit=2) == 0
        session.commit()
        assert session.get(AnalysisHistoryRecord, str(foreign.id)) is not None


def test_registered_private_history_api_uses_actual_postgres(owned_database):
    actor = VerifiedSession(
        issuer="synthetic-api-pg",
        subject="alice",
        email_verified=True,
        mfa_verified=False,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    with get_session_factory()() as session:
        history = AnalysisHistoryService(
            AnalysisHistoryRepository(session),
            policy=HistoryPolicy(
                retention_seconds=3600, approval_reference="synthetic-api-pg-only"
            ),
        )
        saved = history.analyze_and_record(actor, fixture_input())
        session.commit()

    class Adapter:
        async def verify(self, request: Request):
            return actor

    application = create_app()
    configuration = get_settings().model_copy(
        update={
            "history_enabled": True,
            "history_retention_seconds": 3600,
            "history_policy_reference": "synthetic-api-pg-only",
            "history_mutations_enabled": True,
            "history_allowed_origin": AnyHttpUrl("https://frontend.test"),
            "history_audit_retention_seconds": 7200,
            "history_audit_policy_reference": "synthetic-api-pg-audit-only",
        }
    )
    # Only trusted identity/config are synthetic; database dependency is real.
    application.dependency_overrides[get_session_verifier] = Adapter
    application.dependency_overrides[get_settings] = lambda: configuration
    try:
        with TestClient(application) as client:
            page = client.get("/api/v1/history")
            assert page.status_code == 200
            assert page.headers["cache-control"] == "private, no-store"
            assert [item["id"] for item in page.json()["items"]] == [str(saved.id)]
            assert "result_json" not in page.text
            detail = client.get(f"/api/v1/history/{saved.id}")
            assert detail.status_code == 200
            assert detail.json()["result"] == saved.result.model_dump(mode="json")
            denied = client.post(
                "/api/v1/history",
                json=api_payload(),
                headers={"Origin": "https://foreign.test"},
            )
            assert denied.status_code == 403
            created = client.post(
                "/api/v1/history",
                json=api_payload(),
                headers={"Origin": "https://frontend.test"},
            )
            assert created.status_code == 201
            identifier = created.json()["id"]
            deleted = client.delete(
                f"/api/v1/history/{identifier}",
                headers={"Origin": "https://frontend.test"},
            )
            assert deleted.status_code == 204
            assert deleted.content == b""
            assert client.get(f"/api/v1/history/{identifier}").status_code == 404
    finally:
        application.dependency_overrides.clear()


def mutation_actor(subject):
    return VerifiedSession(
        issuer="synthetic-pg-mutations",
        subject=subject,
        email_verified=True,
        mfa_verified=False,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )


def mutation_writer(session):
    return HistoryMutationService(
        session,
        history_policy=HistoryPolicy(
            retention_seconds=3600, approval_reference="synthetic-pg-history"
        ),
        audit_policy=AuditPolicy(
            retention_seconds=7200, approval_reference="synthetic-pg-audit"
        ),
    )


def test_actual_postgres_commits_minimal_audit_with_create_and_delete(owned_database):
    identity = mutation_actor("atomic-success")
    with get_session_factory()() as session:
        entry = mutation_writer(session).create(identity, fixture_input())
    with get_session_factory()() as session:
        rows = session.scalars(
            select(AuditEvent).where(AuditEvent.resource_id == str(entry.id))
        ).all()
        assert len(rows) == 1
        assert rows[0].owner_key == principal_key(identity)
        assert rows[0].action == "analysis_history.created"
        assert rows[0].expires_at - rows[0].occurred_at == timedelta(seconds=7200)
    with get_session_factory()() as session:
        mutation_writer(session).delete(identity, entry.id)
    with get_session_factory()() as session:
        assert session.get(AnalysisHistoryRecord, str(entry.id)) is None
        assert set(
            session.scalars(
                select(AuditEvent.action).where(AuditEvent.resource_id == str(entry.id))
            )
        ) == {"analysis_history.created", "analysis_history.deleted"}


@pytest.mark.parametrize("operation", ["create", "delete"])
def test_actual_audit_constraint_failure_rolls_back_history(
    owned_database, monkeypatch, operation
):
    identity = mutation_actor("atomic-failure-" + operation)
    entry = None
    if operation == "delete":
        with get_session_factory()() as session:
            entry = mutation_writer(session).create(identity, fixture_input())
    with get_session_factory()() as session:
        writer = mutation_writer(session)
        append = writer._audit.append

        def invalid_expiry(record):
            record.expires_at = record.occurred_at
            append(record)

        monkeypatch.setattr(writer._audit, "append", invalid_expiry)
        with pytest.raises(IntegrityError):
            if operation == "create":
                writer.create(identity, fixture_input())
            else:
                writer.delete(identity, entry.id)
    with get_session_factory()() as session:
        owner = principal_key(identity)
        history_count = session.scalar(
            select(func.count())
            .select_from(AnalysisHistoryRecord)
            .where(AnalysisHistoryRecord.owner_key == owner)
        )
        audit_count = session.scalar(
            select(func.count())
            .select_from(AuditEvent)
            .where(AuditEvent.owner_key == owner)
        )
        assert (history_count, audit_count) == (
            (0, 0) if operation == "create" else (1, 1)
        )


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
