"""Add owner-scoped watchlist preferences without changing analytical history."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261030_0004"
down_revision: str | None = "20261030_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "watchlist",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(64), nullable=False),
        sa.Column("pair", sa.String(32), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_reference", sa.String(200), nullable=False),
        sa.UniqueConstraint(
            "owner_key", "pair", "timeframe", name="uq_watchlist_owner_pair"
        ),
        sa.CheckConstraint("expires_at > created_at", name="ck_watchlist_expiry"),
    )
    op.create_index(
        "ix_watchlist_owner_page", "watchlist", ["owner_key", "created_at", "id"]
    )
    op.create_index("ix_watchlist_expiry", "watchlist", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_watchlist_expiry", table_name="watchlist")
    op.drop_index("ix_watchlist_owner_page", table_name="watchlist")
    op.drop_table("watchlist")
