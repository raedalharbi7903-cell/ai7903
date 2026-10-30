"""Real dependency resolution with test-only routers, never public login routes."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from structlog.testing import CapturingLogger

from app.config.settings import Settings, get_settings
from app.core.error_handlers import register_exception_handlers
from app.security.dependencies import (
    get_session_verifier,
    require_customer_session,
    require_founder_session,
)
from app.security.identity import SessionVerificationError, VerifiedSession


def verified_session(**changes: object) -> VerifiedSession:
    values = {
        "issuer": "test-issuer",
        "subject": "founder-subject",
        "email_verified": True,
        "mfa_verified": True,
        "expires_at": datetime.now(UTC) + timedelta(minutes=1),
    }
    return VerifiedSession.model_validate(values | changes)


def client_for(
    session: VerifiedSession | Exception | None = None, **settings: object
) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/customer")
    def customer(
        identity: Annotated[VerifiedSession, Depends(require_customer_session)],
    ) -> dict[str, bool]:
        return {"allowed": bool(identity)}

    @app.get("/command-center")
    def command_center(
        identity: Annotated[VerifiedSession, Depends(require_founder_session)],
    ) -> dict[str, bool]:
        return {"allowed": bool(identity)}

    if session is not None:

        class Adapter:
            async def verify(self, request: object) -> VerifiedSession:
                if isinstance(session, Exception):
                    raise session
                return session

        app.dependency_overrides[get_session_verifier] = Adapter
    configuration = {
        "APP_NAME": "identity-tests",
        "APP_ENVIRONMENT": "testing",
        "LOG_LEVEL": "INFO",
        "DATABASE_URL": "sqlite://",
        "FOUNDER_IDENTITY_ISSUER": "test-issuer",
        "FOUNDER_IDENTITY_SUBJECT": "founder-subject",
    } | settings
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, **configuration
    )
    return TestClient(app, raise_server_exceptions=False)


def test_unconfigured_provider_ignores_forged_headers_and_cookies() -> None:
    with client_for() as client:
        response = client.get(
            "/command-center",
            headers={
                "Authorization": "Bearer forged-secret",
                "X-Role": "founder",
                "X-MFA-Verified": "true",
                "Cookie": "session=forged-secret",
            },
        )
    assert response.status_code == 401
    assert "forged-secret" not in response.text


def test_verified_customer_needs_no_administrative_privileges() -> None:
    session = verified_session(subject="customer", mfa_verified=False)
    with client_for(session) as client:
        assert client.get("/customer").status_code == 200
        assert client.get("/command-center").status_code == 403


def test_only_configured_founder_with_mfa_is_allowed() -> None:
    with client_for(verified_session()) as client:
        assert client.get("/command-center").json() == {"allowed": True}


@pytest.mark.parametrize(
    "changes",
    [
        {"issuer": "other-issuer"},
        {"subject": "other-subject"},
        {"mfa_verified": False},
    ],
)
def test_founder_boundary_denies_untrusted_or_lower_assurance_identity(
    changes: dict[str, object],
) -> None:
    with client_for(verified_session(**changes)) as client:
        assert client.get("/command-center").status_code == 403


@pytest.mark.parametrize(
    "configuration",
    [
        {"FOUNDER_IDENTITY_ISSUER": None},
        {"FOUNDER_IDENTITY_SUBJECT": None},
        {"FOUNDER_IDENTITY_ISSUER": ""},
        {"FOUNDER_IDENTITY_SUBJECT": ""},
    ],
)
def test_missing_founder_enrollment_denies_access(
    configuration: dict[str, object],
) -> None:
    with client_for(verified_session(), **configuration) as client:
        assert client.get("/command-center").status_code == 403


@pytest.mark.parametrize(
    "changes",
    [
        {"email_verified": False},
        {"expires_at": datetime.now(UTC) - timedelta(seconds=1)},
    ],
)
def test_unverified_email_or_expired_session_denied(
    changes: dict[str, object],
) -> None:
    with client_for(verified_session(**changes)) as client:
        assert client.get("/customer").status_code == 401
        assert client.get("/command-center").status_code == 401


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (SessionVerificationError("private-provider-secret"), 401),
        (RuntimeError("private-provider-secret"), 500),
    ],
)
def test_adapter_failures_deny_without_exposing_errors(
    error: Exception,
    expected: int,
) -> None:
    with client_for(error) as client:
        response = client.get("/command-center")
    assert response.status_code == expected
    assert "private-provider-secret" not in response.text


@pytest.mark.parametrize(
    "changes",
    [
        {"mfa_verified": "true"},
        {"email_verified": 1},
        {"subject": ""},
        {"issuer": ""},
        {"expires_at": datetime.now()},
        {"role": "founder"},
    ],
)
def test_session_contract_rejects_untyped_or_unscoped_claims(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        verified_session(**changes)


def test_verified_session_is_immutable() -> None:
    session = verified_session()
    with pytest.raises(ValidationError):
        session.subject = "replacement"


@pytest.mark.parametrize(
    "changes",
    [
        {"mfa_verified": "true"},
        {"mfa_verified": 1},
        {"email_verified": "true"},
        {"email_verified": 1},
        {"issuer": ""},
        {"subject": ""},
        {"expires_at": datetime.now()},
    ],
)
def test_copied_adapter_claims_are_revalidated_before_authorization(changes):
    # Pydantic model_copy deliberately does not validate its update dictionary.
    # A faulty trusted adapter must not turn a truthy string into MFA assurance.
    malformed = verified_session().model_copy(update=changes)
    with client_for(malformed) as client:
        assert client.get("/customer").status_code == 401
        assert client.get("/command-center").status_code == 401


def test_audit_logs_do_not_include_identity_or_credentials(monkeypatch) -> None:
    logger = CapturingLogger()
    monkeypatch.setattr(
        "app.security.dependencies.structlog.get_logger", lambda *_: logger
    )
    with client_for(verified_session()) as client:
        assert client.get("/command-center").status_code == 200
    with client_for(verified_session(mfa_verified=False)) as client:
        assert client.get("/command-center").status_code == 403
    assert [(call.method_name, call.args) for call in logger.calls] == [
        ("info", ("access_granted",)),
        ("warning", ("access_denied",)),
    ]
    output = repr(logger.calls)
    assert "founder-subject" not in output
    assert "test-issuer" not in output
