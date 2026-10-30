"""Real registered history reads with synthetic trusted identities and a real DB."""

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.settings import Settings, get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app
from app.models.analysis_history import AnalysisHistoryRecord
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.security.dependencies import get_session_verifier
from app.security.identity import SessionVerificationError, VerifiedSession
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy
from tests.analysis.test_decision_states import complete_input


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


def test_history_mutations_are_not_accidentally_exposed(history_api):
    client, entries, _, _, _, _ = history_api
    assert client.post("/api/v1/history", headers=ALICE, json={}).status_code == 405
    assert (
        client.delete(f"/api/v1/history/{entries[1].id}", headers=ALICE).status_code
        == 405
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
