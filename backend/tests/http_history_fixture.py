"""Test-only real HTTP history integration; never imported by application code."""

import os
from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.settings import Settings, get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.schemas.billing import VerifiedBillingEvent
from app.security.dependencies import get_session_verifier
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
)
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy
from app.services.billing import BillingPolicy, BillingService
from app.services.history_mutations import AuditPolicy
from tests.analysis.test_decision_states import complete_input

if os.environ.get("APP_ENVIRONMENT") != "testing":
    raise RuntimeError("Refusing synthetic history server outside testing")

engine = create_engine(
    "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)
identity = VerifiedSession(
    issuer="synthetic-http-fixture",
    subject="synthetic-customer",
    email_verified=True,
    mfa_verified=False,
    expires_at=datetime.now(UTC) + timedelta(hours=1),
)
policy = HistoryPolicy(retention_seconds=3600, approval_reference="synthetic-http-only")
with Session(engine) as session:
    history = AnalysisHistoryService(AnalysisHistoryRepository(session), policy=policy)
    history.analyze_and_record(identity, complete_input())
    history.analyze_and_record(
        identity.model_copy(update={"subject": "other-synthetic-customer"}),
        complete_input(),
    )
    session.commit()

billing_identity = identity.model_copy(update={"subject": "synthetic-billing-customer"})
billing_now = datetime.now(UTC)
billing_start = billing_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
billing_end = billing_start.replace(
    year=billing_start.year + (1 if billing_start.month == 12 else 0),
    month=1 if billing_start.month == 12 else billing_start.month + 1,
)
with Session(engine) as session:
    BillingService(
        session,
        policy=BillingPolicy(
            retention_seconds=86400, approval_reference="synthetic-http-billing"
        ),
        audit_policy=AuditPolicy(
            retention_seconds=86400, approval_reference="synthetic-http-billing-audit"
        ),
    ).process_event(
        VerifiedBillingEvent(
            provider="synthetic_billing",
            event_id="synthetic_http_paid",
            owner_key=principal_key(billing_identity),
            kind="paid",
            occurred_at=billing_now,
            paid_period_start=billing_start,
            paid_period_end=billing_end,
            amount_minor=12345,
            currency="SAR",
            renewal_consent=True,
            consent_reference="synthetic-test-only",
        )
    )


class SyntheticVerifier:
    async def verify(self, request: Request) -> VerifiedSession:
        token = request.headers.get("Authorization")
        if token == "Bearer synthetic-history-test":
            return identity
        if token == "Bearer synthetic-save-test":
            return identity.model_copy(update={"subject": "synthetic-save-customer"})
        if token == "Bearer synthetic-watchlist-test":
            return identity.model_copy(
                update={"subject": "synthetic-watchlist-customer"}
            )
        if token == "Bearer synthetic-billing-test":
            return billing_identity
        raise SessionVerificationError


def database():
    with Session(engine) as session:
        yield session


app = create_app()
app.dependency_overrides[get_session_verifier] = SyntheticVerifier
app.dependency_overrides[get_db_session] = database
app.dependency_overrides[get_settings] = lambda: Settings(
    _env_file=None,
    APP_NAME="synthetic-history-http",
    APP_ENVIRONMENT="testing",
    LOG_LEVEL="WARNING",
    DATABASE_URL="sqlite://",
    HISTORY_ENABLED=True,
    HISTORY_MUTATIONS_ENABLED=True,
    HISTORY_ALLOWED_ORIGIN="https://frontend.test",
    HISTORY_AUDIT_RETENTION_SECONDS=7200,
    HISTORY_AUDIT_POLICY_REFERENCE="synthetic-http-audit-only",
    HISTORY_RETENTION_SECONDS=3600,
    HISTORY_POLICY_REFERENCE="synthetic-http-only",
    WATCHLIST_ENABLED=True,
    WATCHLIST_RETENTION_SECONDS=3600,
    WATCHLIST_POLICY_REFERENCE="synthetic-http-watchlist-only",
    WATCHLIST_ALLOWED_ORIGIN="https://frontend.test",
    WATCHLIST_AUDIT_RETENTION_SECONDS=7200,
    WATCHLIST_AUDIT_POLICY_REFERENCE="synthetic-http-watchlist-audit-only",
    BILLING_ENABLED=True,
    BILLING_RETENTION_SECONDS=86400,
    BILLING_POLICY_REFERENCE="synthetic-http-billing",
    BILLING_ALLOWED_ORIGIN="https://frontend.test",
    BILLING_AUDIT_RETENTION_SECONDS=86400,
    BILLING_AUDIT_POLICY_REFERENCE="synthetic-http-billing-audit",
)
