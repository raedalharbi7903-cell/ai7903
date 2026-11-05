"""Actual billing HTTP/core/SQLite flow with a test-only signature verifier."""

import hashlib
import hmac
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
from app.dependencies.billing import MAX_BILLING_EVENT_BYTES, get_billing_event_verifier
from app.main import create_app
from app.models.audit import AuditEvent
from app.models.billing import BillingEventRecord, SubscriptionRecord
from app.repositories.audit import AuditRepository
from app.schemas.billing import VerifiedBillingEvent
from app.security.dependencies import get_session_verifier
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
)
from app.security.payment_events import (
    BillingEventVerificationError,
    BillingEventVerifierUnavailable,
)

ORIGIN = "https://frontend.test"
ALICE = {"Authorization": "Bearer synthetic-alice"}
BOB = {"Authorization": "Bearer synthetic-bob"}
WRITE = {**ALICE, "Origin": ORIGIN}
TEST_KEY = b"synthetic-signature-fixture-not-a-production-key"


def signature(payload: bytes) -> dict[str, str]:
    return {"X-Test-Signature": hmac.new(TEST_KEY, payload, hashlib.sha256).hexdigest()}


@pytest.fixture
def billing_api():
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    now = datetime.now(UTC)
    alice = VerifiedSession(
        issuer="synthetic-billing",
        subject="alice",
        email_verified=True,
        mfa_verified=False,
        expires_at=now + timedelta(hours=1),
    )
    bob = alice.model_copy(update={"subject": "bob"})
    paid = VerifiedBillingEvent(
        provider="synthetic-provider",
        event_id="synthetic-paid-1",
        owner_key=principal_key(alice),
        kind="paid",
        occurred_at=now,
        paid_period_start=now - timedelta(seconds=1),
        paid_period_end=now + timedelta(days=30),
        amount_minor=100,
        currency="SAR",
        renewal_consent=True,
        consent_reference="synthetic-consent",
    )
    state = {
        "settings": Settings(
            _env_file=None,
            APP_NAME="billing-api",
            APP_ENVIRONMENT="testing",
            LOG_LEVEL="WARNING",
            DATABASE_URL="sqlite://",
            BILLING_ENABLED=True,
            BILLING_RETENTION_SECONDS=86400 * 60,
            BILLING_POLICY_REFERENCE="synthetic-only",
            BILLING_ALLOWED_ORIGIN=ORIGIN,
            BILLING_AUDIT_RETENTION_SECONDS=86400 * 60,
            BILLING_AUDIT_POLICY_REFERENCE="synthetic-audit",
            BILLING_PROVIDER_ID="synthetic-provider",
            BILLING_PROVIDER_APPROVAL_REFERENCE="synthetic-provider-only",
        ),
        "event": paid,
        "provider": "synthetic-provider",
        "failure": None,
    }
    calls = []
    opened = []

    class Sessions:
        async def verify(self, request: Request):
            token = request.headers.get("Authorization")
            if token == ALICE["Authorization"]:
                return alice
            if token == BOB["Authorization"]:
                return bob
            if token == "Bearer synthetic-copy":
                return alice.model_copy(update={"email_verified": "true"})
            raise SessionVerificationError

    class Signatures:
        @property
        def provider_id(self):
            return state["provider"]

        async def verify(self, payload, headers):
            calls.append(payload)
            if state["failure"] is not None:
                raise state["failure"]
            expected = signature(payload)["X-Test-Signature"]
            if not hmac.compare_digest(headers.get("x-test-signature", ""), expected):
                raise BillingEventVerificationError("PRIVATE_SIGNATURE_SECRET")
            return state["event"]

    def database():
        opened.append(True)
        with Session(engine) as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_settings] = lambda: state["settings"]
    application.dependency_overrides[get_session_verifier] = Sessions
    application.dependency_overrides[get_billing_event_verifier] = Signatures
    application.dependency_overrides[get_db_session] = database
    with TestClient(application, raise_server_exceptions=False) as client:
        yield client, state, opened, calls, engine, application
    application.dependency_overrides.clear()
    engine.dispose()


def deliver(client, payload=b"synthetic-provider-payload"):
    return client.post(
        "/api/v1/billing/events", content=payload, headers=signature(payload)
    )


def test_real_verified_payment_summary_history_cancel_and_owner_isolation(billing_api):
    client, _, _, calls, engine, _ = billing_api
    before = client.get("/api/v1/billing/subscription", headers=ALICE)
    assert before.status_code == 200
    assert before.json()["state"] == "none" and not before.json()["entitled"]
    response = deliver(client)
    assert response.status_code == 200
    receipt = response.json()
    assert receipt["processing_status"] == "applied" and not receipt["duplicate"]
    assert len(calls) == 1
    duplicate = deliver(client)
    assert duplicate.json() == {**receipt, "duplicate": True}
    summary = client.get("/api/v1/billing/subscription", headers=ALICE)
    assert summary.json()["state"] == "active" and summary.json()["entitled"]
    assert summary.headers["cache-control"] == "private, no-store"
    end = summary.json()["paid_period_end"]
    history = client.get("/api/v1/billing/history", headers=ALICE)
    assert history.status_code == 200
    assert history.headers["cache-control"] == "private, no-store"
    assert len(history.json()["items"]) == 1
    assert "owner_key" not in history.text and "provider_event_id" not in history.text
    assert client.get("/api/v1/billing/history", headers=BOB).json()["items"] == []
    assert (
        client.get("/api/v1/billing/subscription", headers=BOB).json()["state"]
        == "none"
    )
    cancelled = client.post(
        "/api/v1/billing/subscription/cancel", headers=WRITE, json={}
    )
    assert cancelled.status_code == 200
    assert cancelled.headers["cache-control"] == "private, no-store"
    assert cancelled.json()["cancel_at_period_end"]
    assert cancelled.json()["entitled"] and cancelled.json()["paid_period_end"] == end
    assert not cancelled.json()["renewal_consent"]
    repeated = client.post(
        "/api/v1/billing/subscription/cancel", headers=WRITE, json={}
    )
    assert repeated.json() == cancelled.json()
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(BillingEventRecord)) == 1
        assert session.scalar(select(func.count()).select_from(SubscriptionRecord)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == 2


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v1/billing/subscription"),
        ("GET", "/api/v1/billing/history"),
        ("POST", "/api/v1/billing/subscription/cancel"),
    ],
)
def test_customer_endpoints_never_authenticate_client_owner_or_founder_flags(
    method, path
):
    with TestClient(create_app()) as client:
        response = client.request(
            method,
            path,
            headers={"Authorization": "Bearer forged", "X-Role": "founder"},
            json={},
        )
    assert response.status_code == 401


def test_copied_identity_claims_do_not_authenticate_reads(billing_api):
    client, _, opened, _, _, _ = billing_api
    response = client.get(
        "/api/v1/billing/subscription",
        headers={"Authorization": "Bearer synthetic-copy"},
    )
    assert response.status_code == 401 and opened == []


@pytest.mark.parametrize(
    "field",
    [
        "billing_enabled",
        "billing_retention_seconds",
        "billing_policy_reference",
        "billing_audit_retention_seconds",
        "billing_audit_policy_reference",
        "billing_provider_id",
        "billing_provider_approval_reference",
    ],
)
def test_missing_event_configuration_denies_before_stream_and_database(
    billing_api,
    monkeypatch,
    field,
):
    client, state, opened, calls, _, _ = billing_api
    state["settings"] = state["settings"].model_copy(update={field: None})

    def forbidden(*args):
        pytest.fail("Unconfigured webhook must not read the body")

    monkeypatch.setattr(Request, "stream", forbidden)
    response = client.post("/api/v1/billing/events", content=b"PRIVATE_PAYLOAD_SECRET")
    assert response.status_code == 503 and opened == [] and calls == []


def test_unconfigured_verifier_cannot_be_enabled_with_only_settings(
    billing_api, monkeypatch
):
    client, _, opened, calls, _, application = billing_api
    application.dependency_overrides.pop(get_billing_event_verifier)

    def forbidden(*args):
        pytest.fail("Absent reviewed verifier must not read body")

    monkeypatch.setattr(Request, "stream", forbidden)
    response = client.post("/api/v1/billing/events", content=b"PRIVATE_PAYLOAD_SECRET")
    assert response.status_code == 503 and opened == [] and calls == []


def test_verifier_provider_mismatch_denies_before_body(billing_api, monkeypatch):
    client, state, opened, calls, _, _ = billing_api
    state["provider"] = "wrong-provider"

    def forbidden(*args):
        pytest.fail("Wrong provider must not read the body")

    monkeypatch.setattr(Request, "stream", forbidden)
    response = client.post("/api/v1/billing/events", content=b"PRIVATE_PAYLOAD_SECRET")
    assert response.status_code == 503 and opened == [] and calls == []


def test_unsigned_or_wrong_signature_cannot_grant_entitlement(billing_api):
    client, _, opened, _, engine, _ = billing_api
    response = client.post(
        "/api/v1/billing/events",
        json={"kind": "paid", "owner_key": "a" * 64, "amount_minor": 100},
        headers={"X-Test-Signature": "forged", **ALICE, "X-Role": "founder"},
    )
    assert response.status_code == 401 and opened == []
    assert "PRIVATE_" not in response.text
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(BillingEventRecord)) == 0


@pytest.mark.parametrize(
    "failure,status",
    [
        (BillingEventVerificationError("PRIVATE_SIGNATURE_SECRET"), 401),
        (BillingEventVerifierUnavailable("PRIVATE_VENDOR_URL_SECRET"), 503),
        (RuntimeError("PRIVATE_PROVIDER_SECRET"), 503),
    ],
)
def test_verifier_failure_does_not_open_database_or_expose_errors(
    billing_api,
    failure,
    status,
):
    client, state, opened, _, _, _ = billing_api
    state["failure"] = failure
    response = deliver(client)
    assert response.status_code == status and opened == []
    assert "PRIVATE_" not in response.text


@pytest.mark.parametrize(
    "change",
    [
        {"amount_minor": True},
        {"renewal_consent": "true"},
        {"provider": "wrong-provider"},
        {"owner_key": "malformed"},
        {"plan": "annual"},
        {"amount_minor": 9223372036854775808},
    ],
)
def test_copied_invalid_verified_event_denied_before_database(billing_api, change):
    client, state, opened, _, _, _ = billing_api
    state["event"] = state["event"].model_copy(update=change)
    response = deliver(client)
    assert response.status_code == 401 and opened == []


def test_plain_dictionary_cannot_substitute_for_verified_event(billing_api):
    client, state, opened, _, _, _ = billing_api
    state["event"] = state["event"].model_dump()
    assert deliver(client).status_code == 401 and opened == []


@pytest.mark.parametrize("declared_length", [None, "1"])
def test_streaming_payload_limit_not_bypassed_by_chunking_or_false_length(
    billing_api,
    declared_length,
):
    client, _, opened, calls, _, _ = billing_api
    headers = {} if declared_length is None else {"Content-Length": declared_length}
    response = client.post(
        "/api/v1/billing/events",
        content=iter([b"a" * 32768, b"b" * 32768, b"c"]),
        headers=headers,
    )
    assert response.status_code == 413
    assert opened == [] and calls == []


def test_declared_oversized_body_denied_before_reading(billing_api, monkeypatch):
    client, _, opened, calls, _, _ = billing_api

    def forbidden(*args):
        pytest.fail("Declared oversized body must not be consumed")

    monkeypatch.setattr(Request, "stream", forbidden)
    response = client.post(
        "/api/v1/billing/events",
        content=b"x",
        headers={"Content-Length": str(MAX_BILLING_EVENT_BYTES + 1)},
    )
    assert response.status_code == 413 and opened == [] and calls == []


def test_exact_size_opaque_payload_reaches_verifier_without_json_parsing(billing_api):
    client, _, _, calls, _, _ = billing_api
    payload = b"x" * MAX_BILLING_EVENT_BYTES
    assert deliver(client, payload).status_code == 200
    assert calls == [payload]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Origin": "null"},
        {"Origin": "https://foreign.test"},
        {"Origin": ORIGIN, "Sec-Fetch-Site": "cross-site"},
    ],
)
def test_cancellation_origin_boundary_precedes_database(billing_api, headers):
    client, _, opened, _, _, _ = billing_api
    response = client.post(
        "/api/v1/billing/subscription/cancel",
        headers={**ALICE, **headers},
        json={},
    )
    assert response.status_code == 403 and opened == []


@pytest.mark.parametrize(
    "payload",
    [
        {"owner_key": "a" * 64},
        {"role": "founder"},
        {"renewal_consent": True},
        {"refund": True},
        [],
        None,
    ],
)
def test_cancellation_body_cannot_request_other_owner_or_unapproved_actions(
    billing_api,
    payload,
):
    client, _, opened, _, _, _ = billing_api
    response = client.post(
        "/api/v1/billing/subscription/cancel", headers=WRITE, json=payload
    )
    assert response.status_code == 422 and opened == []


@pytest.mark.parametrize(
    "query",
    [
        "?owner=other",
        "?limit=0",
        "?limit=101",
        "?before_id=" + str(uuid4()),
        "?before_created_at=2026-01-01T00:00:00",
    ],
)
def test_billing_history_only_accepts_bounded_owner_free_keyset_query(
    billing_api, query
):
    client, _, _, _, _, _ = billing_api
    assert (
        client.get("/api/v1/billing/history" + query, headers=ALICE).status_code == 422
    )


@pytest.mark.parametrize("operation", ["event", "cancel"])
def test_atomic_audit_failure_has_safe_http_error_and_no_partial_billing_change(
    billing_api,
    monkeypatch,
    operation,
):
    client, _, _, _, engine, _ = billing_api
    if operation == "cancel":
        assert deliver(client).status_code == 200

    def broken(*args):
        raise SQLAlchemyError("PRIVATE_AUDIT_STORAGE_SECRET")

    monkeypatch.setattr(AuditRepository, "append", broken)
    response = (
        deliver(client)
        if operation == "event"
        else client.post("/api/v1/billing/subscription/cancel", headers=WRITE, json={})
    )
    assert response.status_code == 500 and "PRIVATE_" not in response.text
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(BillingEventRecord)) == (
            0 if operation == "event" else 1
        )
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == (
            0 if operation == "event" else 1
        )
        subscription = session.scalar(select(SubscriptionRecord))
        assert (
            subscription is None
            if operation == "event"
            else not subscription.cancel_at_period_end
        )


def test_large_amount_is_serialized_as_exact_decimal_string_not_js_number(billing_api):
    client, state, _, _, _, _ = billing_api
    state["event"] = state["event"].model_copy(
        update={"amount_minor": 9223372036854775807}
    )
    assert deliver(client).status_code == 200
    history = client.get("/api/v1/billing/history", headers=ALICE).json()
    assert history["items"][0]["amount_minor"] == "9223372036854775807"
    assert history["items"][0]["currency"] == "SAR"


def test_public_payload_owner_cannot_override_trusted_adapter_account_mapping(
    billing_api,
):
    client, _, _, _, _, _ = billing_api
    raw = b'{"owner_key":"forged-owner","role":"founder","entitled":true}'
    assert deliver(client, raw).status_code == 200
    assert client.get("/api/v1/billing/subscription", headers=ALICE).json()["entitled"]
    assert not client.get("/api/v1/billing/subscription", headers=BOB).json()[
        "entitled"
    ]


@pytest.mark.parametrize("length", ["-1", "not-a-number", "1, 1", "9" * 4400])
def test_invalid_content_length_is_safe_before_verification_or_database(
    billing_api,
    length,
):
    client, _, opened, calls, _, _ = billing_api
    response = client.post(
        "/api/v1/billing/events", content=b"x", headers={"Content-Length": length}
    )
    assert response.status_code in {400, 413}
    assert opened == [] and calls == []


def test_duplicate_content_length_headers_are_rejected(billing_api):
    client, _, opened, calls, _, _ = billing_api
    response = client.post(
        "/api/v1/billing/events",
        content=b"x",
        headers=[("Content-Length", "1"), ("Content-Length", "2")],
    )
    assert response.status_code == 400 and opened == [] and calls == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("BILLING_RETENTION_SECONDS", 0),
        ("BILLING_AUDIT_RETENTION_SECONDS", -1),
        ("BILLING_POLICY_REFERENCE", " "),
        ("BILLING_AUDIT_POLICY_REFERENCE", ""),
        ("BILLING_PROVIDER_ID", "invalid/provider"),
        ("BILLING_PROVIDER_APPROVAL_REFERENCE", ""),
        ("BILLING_ALLOWED_ORIGIN", "https://user:PRIVATE_SECRET@frontend.test"),
        ("BILLING_ALLOWED_ORIGIN", "https://frontend.test/path"),
    ],
)
def test_invalid_billing_configuration_is_rejected_without_echoing_secret(field, value):
    with pytest.raises(ValueError) as failure:
        Settings(_env_file=None, **{field: value})
    assert "PRIVATE_SECRET" not in str(failure.value)


def test_billing_configuration_has_no_provider_policy_or_price_default(monkeypatch):
    fields = [
        "BILLING_ENABLED",
        "BILLING_RETENTION_SECONDS",
        "BILLING_POLICY_REFERENCE",
        "BILLING_ALLOWED_ORIGIN",
        "BILLING_AUDIT_RETENTION_SECONDS",
        "BILLING_AUDIT_POLICY_REFERENCE",
        "BILLING_PROVIDER_ID",
        "BILLING_PROVIDER_APPROVAL_REFERENCE",
    ]
    for field in fields:
        monkeypatch.delenv(field, raising=False)
    settings = Settings(_env_file=None)
    assert not settings.billing_enabled
    for field in fields[1:]:
        assert getattr(settings, field.lower()) is None
    assert not hasattr(settings, "subscription_price")


def test_openapi_does_not_expose_trusted_event_as_public_request():
    schema = create_app().openapi()
    cancel = schema["paths"]["/api/v1/billing/subscription/cancel"]["post"][
        "requestBody"
    ]
    assert cancel["required"]
    assert (
        cancel["content"]["application/json"]["schema"]["additionalProperties"] is False
    )
    event = schema["paths"]["/api/v1/billing/events"]["post"]["requestBody"]
    assert event["content"]["application/octet-stream"]["schema"]["format"] == "binary"
    assert "VerifiedBillingEvent" not in schema["components"]["schemas"]
