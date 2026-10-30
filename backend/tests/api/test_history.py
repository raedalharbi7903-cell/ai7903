"""Real registered history reads with synthetic trusted identities and a real DB."""

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.settings import Settings, get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app
from app.models.analysis_history import AnalysisHistoryRecord
from app.models.audit import AuditEvent
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.repositories.audit import AuditRepository
from app.security.dependencies import get_session_verifier
from app.security.identity import SessionVerificationError, VerifiedSession
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy
from tests.analysis.test_decision_states import complete_input
from tests.api.test_analysis import payload


@pytest.fixture
def history_api():
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    now = datetime.now(UTC)
    alice = VerifiedSession(
        issuer="synthetic",
        subject="alice",
        email_verified=True,
        mfa_verified=False,
        expires_at=now + timedelta(hours=1),
    )
    bob = alice.model_copy(update={"subject": "bob"})
    policy = HistoryPolicy(retention_seconds=3600, approval_reference="synthetic-only")
    with Session(engine) as session:
        history = AnalysisHistoryService(
            AnalysisHistoryRepository(session), policy=policy, clock=lambda: now
        )
        entries = [
            history.analyze_and_record(alice, complete_input()) for _ in range(5)
        ]
        foreign = history.analyze_and_record(bob, complete_input())
        old = session.get(AnalysisHistoryRecord, str(entries[0].id))
        old.created_at = now - timedelta(seconds=20)
        old.expires_at = now - timedelta(seconds=1)
        session.commit()

    app = create_app()
    state = {
        "settings": Settings(
            _env_file=None,
            APP_NAME="history-api-tests",
            APP_ENVIRONMENT="testing",
            LOG_LEVEL="WARNING",
            DATABASE_URL="sqlite://",
            HISTORY_ENABLED=True,
            HISTORY_RETENTION_SECONDS=3600,
            HISTORY_POLICY_REFERENCE="synthetic-only",
        )
    }
    queries = []

    class Adapter:
        async def verify(self, request: Request):
            token = request.headers.get("Authorization")
            if token == "Bearer synthetic-alice":
                return alice
            if token == "Bearer synthetic-bob":
                return bob
            if token == "Bearer synthetic-mutated":
                return alice.model_copy(update={"email_verified": "true"})
            raise SessionVerificationError

    def database():
        queries.append("database-opened")
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: state["settings"]
    app.dependency_overrides[get_session_verifier] = Adapter
    app.dependency_overrides[get_db_session] = database
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, entries, foreign, state, queries, engine
    app.dependency_overrides.clear()
    engine.dispose()


ALICE = {"Authorization": "Bearer synthetic-alice"}
BOB = {"Authorization": "Bearer synthetic-bob"}


def test_unconfigured_actual_router_never_trusts_client_identity_headers():
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/history",
            headers={
                "Authorization": "Bearer forged",
                "X-Owner": "alice",
                "X-Role": "founder",
            },
        )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
    assert "forged" not in response.text


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer synthetic-mutated"}])
def test_auth_denial_happens_before_any_database_open(history_api, headers):
    client, _, _, _, queries, _ = history_api
    response = client.get("/api/v1/history", headers=headers)
    assert response.status_code == 401
    assert queries == []


@pytest.mark.parametrize(
    "change",
    [
        {"history_enabled": False},
        {"history_retention_seconds": None},
        {"history_policy_reference": None},
    ],
)
def test_release_policy_denial_happens_before_database_access(history_api, change):
    client, _, _, state, queries, _ = history_api
    state["settings"] = state["settings"].model_copy(update=change)
    response = client.get("/api/v1/history", headers=ALICE)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "history_unavailable"
    assert queries == []


def test_actual_pipeline_snapshot_is_private_and_owner_scoped(history_api):
    client, entries, foreign, _, _, _ = history_api
    response = client.get(f"/api/v1/history/{entries[1].id}", headers=ALICE)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    result = response.json()["result"]
    assert result["decision"] == entries[1].result.decision
    assert len(result["outputs"]) == 28
    assert any(o["engine_name"] == "explainability" for o in result["outputs"])
    hidden = client.get(f"/api/v1/history/{foreign.id}", headers=ALICE)
    missing = client.get(f"/api/v1/history/{uuid4()}", headers=ALICE)
    expired = client.get(f"/api/v1/history/{entries[0].id}", headers=ALICE)
    assert [hidden.status_code, missing.status_code, expired.status_code] == [404] * 3
    assert hidden.json() == missing.json() == expired.json()


def test_keyset_page_metadata_excludes_results_and_other_owner(history_api):
    client, entries, foreign, _, _, engine = history_api
    sql = []

    def capture(connection, cursor, statement, parameters, context, executemany):
        sql.append(statement)

    event.listen(engine, "before_cursor_execute", capture)
    try:
        ids = []
        params = {"limit": 2}
        for _ in range(4):
            response = client.get("/api/v1/history", headers=ALICE, params=params)
            assert response.status_code == 200
            assert response.headers["cache-control"] == "private, no-store"
            page = response.json()
            assert page["contract_version"] == "1.0"
            for item in page["items"]:
                assert set(item) == {"id", "created_at", "expires_at"}
            ids.extend(item["id"] for item in page["items"])
            cursor = page["next_cursor"]
            if cursor is None:
                break
            params = {
                "limit": 2,
                "before_created_at": cursor["created_at"],
                "before_id": cursor["id"],
            }
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert set(ids) == {str(entry.id) for entry in entries[1:]}
    assert len(ids) == len(set(ids)) == 4
    assert str(foreign.id) not in ids
    assert all("result_json" not in statement for statement in sql)


@pytest.mark.parametrize(
    "query",
    [
        "limit=0",
        "limit=101",
        "limit=true",
        "limit=2.5",
        "before_id=not-a-uuid",
        "before_created_at=2026-01-01T00:00:00",
        f"before_id={uuid4()}",
        "before_created_at=2026-01-01T00:00:00Z",
        "owner=alice",
        "role=founder",
    ],
)
def test_invalid_or_owner_controlled_query_is_rejected(history_api, query):
    response = history_api[0].get("/api/v1/history?" + query, headers=ALICE)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_cross_account_listing_is_isolated(history_api):
    client, _, foreign, _, _, _ = history_api
    response = client.get("/api/v1/history", headers=BOB)
    assert [item["id"] for item in response.json()["items"]] == [str(foreign.id)]


def test_database_errors_do_not_expose_internal_messages(history_api):
    client, _, _, _, _, engine = history_api
    AnalysisHistoryRecord.__table__.drop(engine)
    response = client.get("/api/v1/history", headers=ALICE)
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "database_error", "message": "A database operation failed"}
    }
    assert "analysis_history" not in response.text


def test_history_mutations_remain_default_disabled(history_api):
    client, entries, _, _, _, _ = history_api
    assert client.post("/api/v1/history", headers=ALICE, json={}).status_code == 503
    assert (
        client.delete(f"/api/v1/history/{entries[1].id}", headers=ALICE).status_code
        == 503
    )


def test_corrupt_snapshot_cannot_invent_a_new_generation_timestamp(history_api):
    client, entries, _, _, _, engine = history_api
    with Session(engine) as session:
        row = session.get(AnalysisHistoryRecord, str(entries[1].id))
        raw = json.loads(row.result_json)
        del raw["generated_at"]
        row.result_json = json.dumps(raw)
        session.commit()
    response = client.get(f"/api/v1/history/{entries[1].id}", headers=ALICE)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "generated_at" not in response.text


WRITE_ORIGIN = "https://frontend.test"
WRITE_ALICE = {**ALICE, "Origin": WRITE_ORIGIN, "Sec-Fetch-Site": "same-origin"}


def enable_writes(state):
    state["settings"] = state["settings"].model_copy(
        update={
            "history_mutations_enabled": True,
            "history_allowed_origin": AnyHttpUrl(WRITE_ORIGIN),
            "history_audit_retention_seconds": 7200,
            "history_audit_policy_reference": "synthetic-audit-only",
        }
    )


def audit_count(engine):
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(AuditEvent))


@pytest.mark.parametrize(
    "change",
    [
        {"history_mutations_enabled": False},
        {"history_allowed_origin": None},
        {"history_audit_retention_seconds": None},
        {"history_audit_policy_reference": None},
    ],
)
def test_write_release_gate_precedes_database_and_analysis(
    history_api, change, monkeypatch
):
    client, _, _, state, queries, engine = history_api
    enable_writes(state)
    state["settings"] = state["settings"].model_copy(update=change)

    def forbidden(*args):
        pytest.fail("Disabled writing must not execute analysis")

    monkeypatch.setattr(
        "app.services.analysis_history.AnalysisService.analyze", forbidden
    )
    response = client.post("/api/v1/history", headers=WRITE_ALICE, json=payload())
    assert response.status_code == 503
    assert queries == []
    assert audit_count(engine) == 0


@pytest.mark.parametrize(
    "origin",
    [
        None,
        "null",
        "https://foreign.test",
        "https://frontend.test.evil.test",
        "http://frontend.test",
        "https://frontend.test/path",
        "https://frontend.test:444",
    ],
)
def test_origin_denial_precedes_database_and_writing(history_api, origin):
    client, _, _, state, queries, engine = history_api
    enable_writes(state)
    headers = dict(ALICE)
    if origin is not None:
        headers["Origin"] = origin
    response = client.post("/api/v1/history", headers=headers, json=payload())
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "history_origin_rejected"
    assert queries == []
    assert audit_count(engine) == 0


def test_multiple_origins_or_cross_site_fetch_are_rejected(history_api):
    client, _, _, state, queries, _ = history_api
    enable_writes(state)
    duplicate = client.post(
        "/api/v1/history",
        json=payload(),
        headers=[
            ("Authorization", ALICE["Authorization"]),
            ("Origin", WRITE_ORIGIN),
            ("Origin", "https://foreign.test"),
        ],
    )
    cross_site = client.post(
        "/api/v1/history",
        json=payload(),
        headers={
            **WRITE_ALICE,
            "Sec-Fetch-Site": "cross-site",
        },
    )
    assert duplicate.status_code == cross_site.status_code == 403
    assert queries == []


def test_explicit_analyze_save_and_owned_delete_are_audited_atomically(
    history_api, monkeypatch
):
    client, _, _, state, _, engine = history_api
    enable_writes(state)
    from app.analysis.service import AnalysisService

    original = AnalysisService.analyze
    executions = []

    def count_analysis(self, source):
        executions.append(True)
        return original(self, source)

    monkeypatch.setattr(AnalysisService, "analyze", count_analysis)
    created = client.post("/api/v1/history", json=payload(), headers=WRITE_ALICE)
    assert created.status_code == 201
    assert created.headers["cache-control"] == "private, no-store"
    entry = created.json()
    assert len(entry["result"]["outputs"]) == 28
    assert len(executions) == 1
    assert audit_count(engine) == 1
    assert (
        client.get(f"/api/v1/history/{entry['id']}", headers=ALICE).status_code == 200
    )
    denied = client.delete(
        f"/api/v1/history/{entry['id']}",
        headers={
            **BOB,
            "Origin": WRITE_ORIGIN,
        },
    )
    assert denied.status_code == 404
    assert audit_count(engine) == 1
    deleted = client.delete(f"/api/v1/history/{entry['id']}", headers=WRITE_ALICE)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert deleted.headers["cache-control"] == "private, no-store"
    assert audit_count(engine) == 2
    assert len(executions) == 1
    assert (
        client.get(f"/api/v1/history/{entry['id']}", headers=ALICE).status_code == 404
    )


@pytest.mark.parametrize("operation", ["create", "delete"])
def test_api_audit_failure_cannot_leave_a_partial_data_change(
    history_api, monkeypatch, operation
):
    client, entries, _, state, _, engine = history_api
    enable_writes(state)

    def broken(*args):
        raise SQLAlchemyError("PRIVATE_AUDIT_SECRET")

    monkeypatch.setattr(AuditRepository, "append", broken)
    if operation == "create":
        response = client.post("/api/v1/history", json=payload(), headers=WRITE_ALICE)
    else:
        response = client.delete(
            f"/api/v1/history/{entries[1].id}", headers=WRITE_ALICE
        )
    assert response.status_code == 500
    assert "PRIVATE_AUDIT_SECRET" not in response.text
    with Session(engine) as session:
        assert (
            session.scalar(select(func.count()).select_from(AnalysisHistoryRecord)) == 6
        )
    assert audit_count(engine) == 0


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_fixture_save_cannot_bypass_original_environment_gate(history_api, environment):
    client, _, _, state, _, engine = history_api
    enable_writes(state)
    state["settings"] = state["settings"].model_copy(
        update={"environment": environment}
    )
    response = client.post("/api/v1/history", json=payload(), headers=WRITE_ALICE)
    assert response.status_code == 503
    assert audit_count(engine) == 0


@pytest.mark.parametrize("field", ["result", "owner", "role"])
def test_saved_analysis_never_accepts_a_client_result_or_owner(history_api, field):
    client, _, _, state, _, engine = history_api
    enable_writes(state)
    response = client.post(
        "/api/v1/history",
        headers=WRITE_ALICE,
        json={
            **payload(),
            field: "untrusted-client-value",
        },
    )
    assert response.status_code == 422
    assert audit_count(engine) == 0
