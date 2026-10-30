"""Add owner-scoped analysis history; runtime writes remain explicitly gated."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261030_0002"
down_revision: str | None = "20260725_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_reference", sa.String(200), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "expires_at > created_at", name="ck_analysis_history_expiry"
        ),
    )
    op.create_index(
        "ix_analysis_history_owner_page",
        "analysis_history",
        ["owner_key", "created_at", "id"],
    )
    op.create_index("ix_analysis_history_expiry", "analysis_history", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_analysis_history_expiry", table_name="analysis_history")
    op.drop_index("ix_analysis_history_owner_page", table_name="analysis_history")
    op.drop_table("analysis_history")
