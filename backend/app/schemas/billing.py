"""Minimal customer DTOs and a trusted-adapter event contract, not webhook auth.

Constructing VerifiedBillingEvent does not verify signatures or account mapping.
No public route may deserialize request JSON into it and treat that as trust.
"""

from datetime import timedelta
from typing import Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.history import HistoryCursor, HistoryQuery


class BillingContract(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class VerifiedBillingEvent(BillingContract):
    """Only a reviewed signature/account-mapping adapter may supply this object."""

    provider: str = Field(pattern=r"^[a-z0-9_-]{1,64}$")
    event_id: str = Field(pattern=r"^[A-Za-z0-9._:-]{1,200}$")
    owner_key: str = Field(pattern=r"^[a-f0-9]{64}$")
    kind: Literal["paid", "payment_failed", "refund", "dispute", "unsupported"]
    occurred_at: AwareDatetime
    plan: Literal["monthly"] = "monthly"
    paid_period_start: AwareDatetime | None = None
    paid_period_end: AwareDatetime | None = None
    amount_minor: int | None = Field(default=None, gt=0, le=9223372036854775807)
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    renewal_consent: bool = False
    consent_reference: str | None = Field(
        default=None, min_length=1, max_length=200, pattern=r"\S"
    )

    @field_validator("occurred_at", "paid_period_start", "paid_period_end")
    @classmethod
    def explicit_utc(cls, value):
        if value is not None and value.utcoffset() != timedelta(0):
            raise ValueError("Billing event timestamps must be explicit UTC")
        return value

    @model_validator(mode="after")
    def coherent_event(self) -> "VerifiedBillingEvent":
        if (self.paid_period_start is None) != (self.paid_period_end is None):
            raise ValueError("Paid period bounds must be supplied together")
        if self.paid_period_start is not None and not (
            self.paid_period_start < self.paid_period_end
        ):
            raise ValueError("Paid period must be positive")
        if (self.amount_minor is None) != (self.currency is None):
            raise ValueError("Money amount/currency must be supplied together")
        if self.kind == "paid" and (
            self.paid_period_start is None or self.amount_minor is None
        ):
            raise ValueError("Paid events need an explicit period and money amount")
        if self.renewal_consent and self.consent_reference is None:
            raise ValueError("Renewal consent requires a verified consent reference")
        if not self.renewal_consent and self.consent_reference is not None:
            raise ValueError("Consent reference cannot imply missing consent")
        return self


class SubscriptionSummary(BillingContract):
    contract_version: Literal["1.0"] = "1.0"
    plan: Literal["monthly"] = "monthly"
    state: Literal["none", "active", "scheduled", "expired", "review_required"]
    entitled: bool
    paid_period_start: AwareDatetime | None
    paid_period_end: AwareDatetime | None
    cancel_at_period_end: bool
    renewal_consent: bool
    review_required: bool


class BillingEventReceipt(BillingContract):
    id: UUID
    processing_status: Literal["applied", "review_required"]
    duplicate: bool


class BillingHistoryQuery(HistoryQuery):
    """Existing owner-free keyset contract over recorded_at, not event time."""


class BillingHistoryItem(BillingContract):
    id: UUID
    kind: Literal["paid", "payment_failed", "refund", "dispute", "unsupported"]
    amount_minor: str | None = Field(default=None, pattern=r"^[1-9][0-9]{0,18}$")
    currency: str | None
    recorded_at: AwareDatetime
    retained_until: AwareDatetime
    processing_status: Literal["applied", "review_required"]

    @field_validator("amount_minor")
    @classmethod
    def bounded_lossless_amount(cls, value):
        if value is not None and int(value) > 9223372036854775807:
            raise ValueError("Minor-unit amount exceeds signed 64-bit range")
        return value


class BillingHistoryPage(BillingContract):
    contract_version: Literal["1.0"] = "1.0"
    items: list[BillingHistoryItem]
    next_cursor: HistoryCursor | None
