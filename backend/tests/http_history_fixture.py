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
from app.security.dependencies import get_session_verifier
from app.security.identity import SessionVerificationError, VerifiedSession
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy
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


class SyntheticVerifier:
    async def verify(self, request: Request) -> VerifiedSession:
        token = request.headers.get("Authorization")
        if token == "Bearer synthetic-history-test":
            return identity
        if token == "Bearer synthetic-save-test":
            return identity.model_copy(update={"subject": "synthetic-save-customer"})
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
)
