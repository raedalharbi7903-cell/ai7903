"""Trusted payment-adapter boundary, never a public JSON trust constructor.

No vendor, key, signature scheme or network adapter is selected here. An approved
adapter must verify exact payload signatures, timestamp/replay policy and account
mapping before returning a VerifiedBillingEvent.
"""

from collections.abc import Mapping
from typing import Protocol

from app.schemas.billing import VerifiedBillingEvent


class BillingEventVerificationError(Exception):
    """Signature, timestamp, replay or trusted-account mapping is invalid."""


class BillingEventVerifierUnavailable(Exception):
    """A trusted verifier cannot safely establish event authenticity."""


class BillingEventVerifier(Protocol):
    @property
    def provider_id(self) -> str: ...

    async def verify(
        self, payload: bytes, headers: Mapping[str, str]
    ) -> VerifiedBillingEvent: ...


class UnconfiguredBillingEventVerifier:
    provider_id = "unconfigured"

    async def verify(
        self, payload: bytes, headers: Mapping[str, str]
    ) -> VerifiedBillingEvent:
        raise BillingEventVerifierUnavailable
