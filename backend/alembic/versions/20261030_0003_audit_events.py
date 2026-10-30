"""Add minimal atomic audit records for explicit history mutations."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261030_0003"
down_revision: str | None = "20261030_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_reference", sa.String(200), nullable=False),
        sa.CheckConstraint("expires_at > occurred_at", name="ck_audit_events_expiry"),
    )
    op.create_index(
        "ix_audit_events_owner_time", "audit_events", ["owner_key", "occurred_at"]
    )
    op.create_index("ix_audit_events_expiry", "audit_events", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_expiry", table_name="audit_events")
    op.drop_index("ix_audit_events_owner_time", table_name="audit_events")
    op.drop_table("audit_events")
