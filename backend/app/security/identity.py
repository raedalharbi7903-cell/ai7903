"""Trusted adapter contract, never populated directly from public request data."""

from typing import Protocol

from fastapi import Request
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


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
