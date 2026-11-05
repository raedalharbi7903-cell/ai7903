"""Pseudonymous monthly access windows and minimal normalized billing ledger."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SubscriptionRecord(Base):
    __tablename__ = "billing_subscriptions"
    __table_args__ = (
        UniqueConstraint("owner_key", name="uq_billing_owner"),
        CheckConstraint("plan = 'monthly'", name="ck_billing_monthly"),
        CheckConstraint(
            "(paid_period_start IS NULL AND paid_period_end IS NULL) OR "
            "(paid_period_start IS NOT NULL AND paid_period_end IS NOT NULL AND "
            "paid_period_end > paid_period_start)",
            name="ck_billing_paid_window",
        ),
        CheckConstraint("version > 0", name="ck_billing_version"),
        CheckConstraint(
            "NOT renewal_consent OR consent_reference IS NOT NULL",
            name="ck_billing_consent_reference",
        ),
        CheckConstraint(
            "NOT cancel_at_period_end OR NOT renewal_consent",
            name="ck_billing_cancelled_consent",
        ),
        CheckConstraint("retained_until > created_at", name="ck_billing_retention"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_key: Mapped[str] = mapped_column(String(64), nullable=False)
    plan: Mapped[str] = mapped_column(String(16), nullable=False)
    paid_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, nullable=False)
    renewal_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    consent_reference: Mapped[str | None] = mapped_column(String(200))
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    retained_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    policy_reference: Mapped[str] = mapped_column(String(200), nullable=False)

    __mapper_args__ = {"version_id_col": version}


class BillingEventRecord(Base):
    __tablename__ = "billing_events"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_event_id", name="uq_billing_provider_event"
        ),
        CheckConstraint(
            "retained_until > recorded_at", name="ck_billing_event_retention"
        ),
        CheckConstraint(
            "amount_minor IS NULL OR amount_minor > 0", name="ck_billing_event_amount"
        ),
        CheckConstraint(
            "(amount_minor IS NULL AND currency IS NULL) OR "
            "(amount_minor IS NOT NULL AND currency IS NOT NULL)",
            name="ck_billing_event_money_pair",
        ),
        CheckConstraint(
            "(paid_period_start IS NULL AND paid_period_end IS NULL) OR "
            "(paid_period_start IS NOT NULL AND paid_period_end IS NOT NULL AND "
            "paid_period_end > paid_period_start)",
            name="ck_billing_event_window",
        ),
        CheckConstraint(
            "kind != 'paid' OR (paid_period_start IS NOT NULL "
            "AND amount_minor IS NOT NULL)",
            name="ck_billing_event_paid_fields",
        ),
        CheckConstraint(
            "processing_status IN ('applied', 'review_required')",
            name="ck_billing_event_status",
        ),
        CheckConstraint(
            "kind IN ('paid', 'payment_failed', 'refund', 'dispute', 'unsupported')",
            name="ck_billing_event_kind",
        ),
        Index("ix_billing_events_owner_page", "owner_key", "recorded_at", "id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_key: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_event_id: Mapped[str] = mapped_column(String(200), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    retained_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    policy_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_minor: Mapped[int | None] = mapped_column(BigInteger)
    currency: Mapped[str | None] = mapped_column(String(3))
    paid_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False)
    review_reason: Mapped[str | None] = mapped_column(String(64))
