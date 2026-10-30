"""Registered watchlist API, synthetic trusted sessions and real persistence."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.settings import Settings, get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app
from app.models.audit import AuditEvent
from app.models.watchlist import WatchlistRecord
from app.repositories.audit import AuditRepository
from app.security.dependencies import get_session_verifier
from app.security.identity import SessionVerificationError, VerifiedSession

ORIGIN = "https://frontend.test"
ALICE = {"Authorization": "Bearer synthetic-alice"}
WRITE = {**ALICE, "Origin": ORIGIN}
INPUT = {"pair": "BTC-USDT", "timeframe": "1h"}


@pytest.fixture
def api():
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    state = {
        "settings": Settings(
            _env_file=None,
            APP_NAME="watchlist",
            APP_ENVIRONMENT="testing",
            LOG_LEVEL="WARNING",
            DATABASE_URL="sqlite://",
            WATCHLIST_ENABLED=True,
            WATCHLIST_RETENTION_SECONDS=3600,
            WATCHLIST_POLICY_REFERENCE="synthetic-only",
            WATCHLIST_ALLOWED_ORIGIN=ORIGIN,
            WATCHLIST_AUDIT_RETENTION_SECONDS=7200,
            WATCHLIST_AUDIT_POLICY_REFERENCE="synthetic-audit-only",
        )
    }
    opened = []

    class Adapter:
        async def verify(self, request: Request):
            token = request.headers.get("Authorization")
            if token not in {"Bearer synthetic-alice", "Bearer synthetic-bob"}:
                raise SessionVerificationError
            return VerifiedSession(
                issuer="synthetic-only",
                subject=token.split("-")[-1],
                email_verified=True,
                mfa_verified=False,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            )

    def database():
        opened.append(True)
        with Session(engine) as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_session_verifier] = Adapter
    application.dependency_overrides[get_settings] = lambda: state["settings"]
    application.dependency_overrides[get_db_session] = database
    with TestClient(application, raise_server_exceptions=False) as client:
        yield client, state, opened, engine
    application.dependency_overrides.clear()
    engine.dispose()


def test_actual_default_app_does_not_accept_client_roles_or_test_tokens():
    with TestClient(create_app()) as client:
        for method, path in (
            ("GET", "/api/v1/watchlist"),
            ("POST", "/api/v1/watchlist"),
            ("DELETE", "/api/v1/watchlist/" + str(uuid4())),
        ):
            response = client.request(
                method,
                path,
                headers={**WRITE, "X-Role": "founder"},
                json=INPUT,
            )
            assert response.status_code == 401


def test_save_list_duplicate_and_owned_delete_use_real_db_and_audit(api, monkeypatch):
    client, _, _, engine = api

    def forbidden(*args):
        pytest.fail("Watchlists must never execute analysis")

    monkeypatch.setattr("app.analysis.service.AnalysisService.analyze", forbidden)
    assert client.get("/api/v1/watchlist", headers=ALICE).json()["items"] == []
    created = client.post("/api/v1/watchlist", headers=WRITE, json=INPUT)
    assert created.status_code == 201
    entry = created.json()
    assert created.headers["cache-control"] == "private, no-store"
    duplicate = client.post("/api/v1/watchlist", headers=WRITE, json=INPUT)
    assert duplicate.status_code == 200
    assert duplicate.json() == entry
    assert client.get("/api/v1/watchlist", headers=ALICE).json()["items"] == [entry]
    assert (
        client.get(
            "/api/v1/watchlist", headers={"Authorization": "Bearer synthetic-bob"}
        ).json()["items"]
        == []
    )
    other = client.delete(
        "/api/v1/watchlist/" + entry["id"],
        headers={"Authorization": "Bearer synthetic-bob", "Origin": ORIGIN},
    )
    assert other.status_code == 404
    removed = client.delete("/api/v1/watchlist/" + entry["id"], headers=WRITE)
    assert removed.status_code == 204 and removed.content == b""
    assert removed.headers["cache-control"] == "private, no-store"
    assert (
        client.delete("/api/v1/watchlist/" + entry["id"], headers=WRITE).status_code
        == 404
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(WatchlistRecord)) == 0
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == 2


@pytest.mark.parametrize(
    "change",
    [
        {"watchlist_enabled": False},
        {"watchlist_retention_seconds": None},
        {"watchlist_policy_reference": None},
        {"watchlist_allowed_origin": None},
        {"watchlist_audit_retention_seconds": None},
        {"watchlist_audit_policy_reference": None},
    ],
)
def test_missing_write_gate_precedes_database(api, change):
    client, state, opened, _ = api
    state["settings"] = state["settings"].model_copy(update=change)
    response = client.post("/api/v1/watchlist", headers=WRITE, json=INPUT)
    assert response.status_code == 503
    assert opened == []


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
def test_untrusted_origin_denied_before_database(api, origin):
    client, _, opened, _ = api
    headers = dict(ALICE)
    if origin is not None:
        headers["Origin"] = origin
    assert (
        client.post("/api/v1/watchlist", headers=headers, json=INPUT).status_code == 403
    )
    assert opened == []


def test_duplicate_origins_and_cross_site_fetch_denied(api):
    client, _, opened, _ = api
    duplicate = list(WRITE.items()) + [("Origin", "https://foreign.test")]
    assert (
        client.post("/api/v1/watchlist", headers=duplicate, json=INPUT).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/watchlist",
            headers={**WRITE, "Sec-Fetch-Site": "cross-site"},
            json=INPUT,
        ).status_code
        == 403
    )
    assert opened == []


@pytest.mark.parametrize(
    "payload",
    [
        {"pair": "btc-usdt", "timeframe": "1h"},
        {"pair": "BTC/USDT", "timeframe": "1h"},
        {"pair": "BTC-USDT", "timeframe": "fixture"},
        {"pair": "BTC-USDT", "timeframe": "bogus"},
        {"pair": "BTC-USDT", "timeframe": "1h", "owner": "bob"},
        {"pair": "BTC-USDT", "timeframe": "1h", "role": "founder"},
        {"pair": "BTC-USDT", "timeframe": "1h", "market": "futures"},
    ],
)
def test_pair_timeframe_and_extra_fields_are_validated(api, payload):
    client, _, _, _ = api
    assert (
        client.post("/api/v1/watchlist", headers=WRITE, json=payload).status_code == 422
    )


@pytest.mark.parametrize(
    "query",
    [
        "?limit=0",
        "?limit=101",
        "?before_id=" + str(uuid4()),
        "?before_created_at=2026-10-30T00:00:00",
        "?owner=bob",
    ],
)
def test_query_cursor_limit_and_owner_input_rejected(api, query):
    client, _, _, _ = api
    assert client.get("/api/v1/watchlist" + query, headers=ALICE).status_code == 422


@pytest.mark.parametrize("operation", ["create", "delete"])
def test_audit_failure_is_safe_and_rolls_back_http_mutation(
    api, monkeypatch, operation
):
    client, _, _, engine = api
    original = client.post("/api/v1/watchlist", headers=WRITE, json=INPUT)
    assert original.status_code == 201
    item = original.json()

    def broken(*args):
        raise SQLAlchemyError("PRIVATE_WATCHLIST_STORAGE_SECRET")

    monkeypatch.setattr(AuditRepository, "append", broken)
    if operation == "create":
        response = client.post(
            "/api/v1/watchlist",
            headers=WRITE,
            json={"pair": "ETH-USDT", "timeframe": "1h"},
        )
    else:
        response = client.delete("/api/v1/watchlist/" + item["id"], headers=WRITE)
    assert response.status_code == 500
    assert "PRIVATE_WATCHLIST_STORAGE_SECRET" not in response.text
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(WatchlistRecord)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == 1


@pytest.mark.parametrize(
    "origin",
    [
        "http://foreign.test",
        "https://frontend.test/path",
        "https://user:secret@frontend.test",
        "https://*.frontend.test",
        "https://frontend.test?query=1",
    ],
)
def test_unsafe_watchlist_origin_cannot_be_configured(origin):
    with pytest.raises(ValueError):
        Settings(_env_file=None, WATCHLIST_ALLOWED_ORIGIN=origin)


def test_unset_watchlist_configuration_has_no_implicit_policy(monkeypatch):
    for key in (
        "WATCHLIST_ENABLED",
        "WATCHLIST_RETENTION_SECONDS",
        "WATCHLIST_POLICY_REFERENCE",
        "WATCHLIST_ALLOWED_ORIGIN",
        "WATCHLIST_AUDIT_RETENTION_SECONDS",
        "WATCHLIST_AUDIT_POLICY_REFERENCE",
    ):
        monkeypatch.delenv(key, raising=False)
    settings = Settings(_env_file=None)
    assert not settings.watchlist_enabled
    assert settings.watchlist_retention_seconds is None
    assert settings.watchlist_policy_reference is None
    assert settings.watchlist_allowed_origin is None
    assert settings.watchlist_audit_retention_seconds is None
    assert settings.watchlist_audit_policy_reference is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("WATCHLIST_RETENTION_SECONDS", 0),
        ("WATCHLIST_AUDIT_RETENTION_SECONDS", -1),
        ("WATCHLIST_POLICY_REFERENCE", " "),
        ("WATCHLIST_AUDIT_POLICY_REFERENCE", ""),
    ],
)
def test_invalid_watchlist_policy_configuration_rejected(field, value):
    with pytest.raises(ValueError):
        Settings(_env_file=None, **{field: value})


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_loopback_http_watchlist_origin_is_development_only(environment):
    with pytest.raises(ValueError):
        Settings(
            _env_file=None,
            APP_ENVIRONMENT=environment,
            WATCHLIST_ALLOWED_ORIGIN="http://127.0.0.1:5173",
        )


def test_delete_cannot_skip_origin_and_expired_item_is_not_disclosed(api):
    client, _, _, engine = api
    created = client.post("/api/v1/watchlist", headers=WRITE, json=INPUT)
    assert created.status_code == 201
    identifier = created.json()["id"]
    assert (
        client.delete("/api/v1/watchlist/" + identifier, headers=ALICE).status_code
        == 403
    )
    with Session(engine) as session:
        row = session.get(WatchlistRecord, identifier)
        row.created_at = datetime.now(UTC) - timedelta(hours=2)
        row.expires_at = datetime.now(UTC) - timedelta(hours=1)
        session.commit()
    assert client.get("/api/v1/watchlist", headers=ALICE).json()["items"] == []
    expired = client.delete("/api/v1/watchlist/" + identifier, headers=WRITE)
    missing = client.delete("/api/v1/watchlist/" + str(uuid4()), headers=WRITE)
    assert expired.status_code == missing.status_code == 404
    assert expired.json() == missing.json()
