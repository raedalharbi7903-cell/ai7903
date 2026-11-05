"""Add gated provider-neutral subscriptions and minimal normalized billing events."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261105_0005"
down_revision: str | None = "20261030_0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "billing_subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(64), nullable=False),
        sa.Column("plan", sa.String(16), nullable=False),
        sa.Column("paid_period_start", sa.DateTime(timezone=True)),
        sa.Column("paid_period_end", sa.DateTime(timezone=True)),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False),
        sa.Column("renewal_consent", sa.Boolean(), nullable=False),
        sa.Column("consent_reference", sa.String(200)),
        sa.Column("review_required", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retained_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_reference", sa.String(200), nullable=False),
        sa.UniqueConstraint("owner_key", name="uq_billing_owner"),
        sa.CheckConstraint("plan = 'monthly'", name="ck_billing_monthly"),
        sa.CheckConstraint(
            "(paid_period_start IS NULL AND paid_period_end IS NULL) OR "
            "(paid_period_start IS NOT NULL AND paid_period_end IS NOT NULL AND "
            "paid_period_end > paid_period_start)",
            name="ck_billing_paid_window",
        ),
        sa.CheckConstraint("version > 0", name="ck_billing_version"),
        sa.CheckConstraint(
            "NOT renewal_consent OR consent_reference IS NOT NULL",
            name="ck_billing_consent_reference",
        ),
        sa.CheckConstraint(
            "NOT cancel_at_period_end OR NOT renewal_consent",
            name="ck_billing_cancelled_consent",
        ),
        sa.CheckConstraint("retained_until > created_at", name="ck_billing_retention"),
    )
    op.create_table(
        "billing_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("provider_event_id", sa.String(200), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retained_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_reference", sa.String(200), nullable=False),
        sa.Column("amount_minor", sa.BigInteger()),
        sa.Column("currency", sa.String(3)),
        sa.Column("paid_period_start", sa.DateTime(timezone=True)),
        sa.Column("paid_period_end", sa.DateTime(timezone=True)),
        sa.Column("processing_status", sa.String(32), nullable=False),
        sa.Column("review_reason", sa.String(64)),
        sa.UniqueConstraint(
            "provider", "provider_event_id", name="uq_billing_provider_event"
        ),
        sa.CheckConstraint(
            "retained_until > recorded_at", name="ck_billing_event_retention"
        ),
        sa.CheckConstraint(
            "amount_minor IS NULL OR amount_minor > 0", name="ck_billing_event_amount"
        ),
        sa.CheckConstraint(
            "(amount_minor IS NULL AND currency IS NULL) OR "
            "(amount_minor IS NOT NULL AND currency IS NOT NULL)",
            name="ck_billing_event_money_pair",
        ),
        sa.CheckConstraint(
            "(paid_period_start IS NULL AND paid_period_end IS NULL) OR "
            "(paid_period_start IS NOT NULL AND paid_period_end IS NOT NULL AND "
            "paid_period_end > paid_period_start)",
            name="ck_billing_event_window",
        ),
        sa.CheckConstraint(
            "kind != 'paid' OR (paid_period_start IS NOT NULL "
            "AND amount_minor IS NOT NULL)",
            name="ck_billing_event_paid_fields",
        ),
        sa.CheckConstraint(
            "processing_status IN ('applied', 'review_required')",
            name="ck_billing_event_status",
        ),
        sa.CheckConstraint(
            "kind IN ('paid', 'payment_failed', 'refund', 'dispute', 'unsupported')",
            name="ck_billing_event_kind",
        ),
    )
    op.create_index(
        "ix_billing_events_owner_page",
        "billing_events",
        ["owner_key", "recorded_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_billing_events_owner_page", table_name="billing_events")
    op.drop_table("billing_events")
    op.drop_table("billing_subscriptions")
