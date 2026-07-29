"""Initial schema revision; no business tables yet."""

from collections.abc import Sequence

revision: str = "20260725_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Establish Alembic revision tracking only."""


def downgrade() -> None:
    """Revert the empty initial revision."""
