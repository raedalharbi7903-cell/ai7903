"""Trusted adapter contract, never populated directly from public request data."""

import hashlib
import json
from datetime import datetime
from typing import Protocol

from fastapi import Request
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationError
from pydantic_core import PydanticSerializationError


class VerifiedSession(BaseModel):
    """A provider-verified, unrevoked session, not a client identity assertion."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    issuer: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    email_verified: bool
    mfa_verified: bool
    expires_at: AwareDatetime


class SessionVerificationError(Exception):
    """Authentication is missing, invalid, revoked, or temporarily unavailable."""


def validate_customer_session(value: object, now: datetime) -> VerifiedSession:
    """Revalidate adapter output; model_copy/model_construct can bypass validation.

    This checks the local claim contract, not signatures, revocation or vendor
    assurance. Those remain the trusted SessionVerifier's responsibility.
    """
    if not isinstance(value, VerifiedSession):
        raise SessionVerificationError
    try:
        session = VerifiedSession.model_validate(value.model_dump(warnings="error"))
    except (ValidationError, PydanticSerializationError) as error:
        raise SessionVerificationError from error
    if not session.email_verified or session.expires_at <= now:
        raise SessionVerificationError
    return session


def principal_key(session: VerifiedSession) -> str:
    """Stable pseudonymous key for already validated issuer/subject claims.

    Preserve the original history key encoding so existing owner scope is stable.
    This is neither authentication nor anonymity; validate before calling.
    """
    principal = json.dumps([session.issuer, session.subject], ensure_ascii=False)
    return hashlib.sha256(principal.encode("utf-8")).hexdigest()


class SessionVerifier(Protocol):
    """Validate credentials, issuer/audience, revocation and assurance server-side.

    Adapters must not trust client-supplied roles or MFA flags. Cookie adapters
    must also enforce CSRF defenses for state-changing requests.
    """

    async def verify(self, request: Request) -> VerifiedSession: ...


class UnconfiguredSessionVerifier:
    """Default deny; selecting a vendor must be an explicit future integration."""

    async def verify(self, request: Request) -> VerifiedSession:
        raise SessionVerificationError
