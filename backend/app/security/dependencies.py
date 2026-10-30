"""Fail-closed access dependencies for future protected routers."""

from datetime import UTC, datetime
from typing import Annotated, NoReturn

import structlog
from fastapi import Depends, Request

from app.config.settings import Settings, get_settings
from app.core.exceptions import APIError
from app.security.identity import (
    SessionVerificationError,
    SessionVerifier,
    UnconfiguredSessionVerifier,
    VerifiedSession,
    validate_customer_session,
)


def get_session_verifier() -> SessionVerifier:
    return UnconfiguredSessionVerifier()


def _deny(status: int, code: str) -> NoReturn:
    # Never log credentials, emails, session identifiers or raw adapter errors.
    structlog.get_logger(__name__).warning("access_denied", reason=code)
    raise APIError(status, code, "Access denied")


async def require_customer_session(
    request: Request,
    verifier: Annotated[SessionVerifier, Depends(get_session_verifier)],
) -> VerifiedSession:
    try:
        session = await verifier.verify(request)
        return validate_customer_session(session, datetime.now(UTC))
    except SessionVerificationError:
        _deny(401, "authentication_required")


def require_founder_session(
    session: Annotated[VerifiedSession, Depends(require_customer_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VerifiedSession:
    if (
        not settings.founder_identity_issuer
        or not settings.founder_identity_subject
        or session.issuer != settings.founder_identity_issuer
        or session.subject != settings.founder_identity_subject
        or not session.mfa_verified
    ):
        _deny(403, "founder_access_required")
    structlog.get_logger(__name__).info(
        "access_granted", boundary="founder", assurance="mfa"
    )
    return session
