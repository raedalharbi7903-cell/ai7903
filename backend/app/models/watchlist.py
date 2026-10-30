"""Owner-scoped, expiring pair/timeframe preferences without analytical output."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WatchlistRecord(Base):
    __tablename__ = "watchlist"
    __table_args__ = (
        UniqueConstraint(
            "owner_key", "pair", "timeframe", name="uq_watchlist_owner_pair"
        ),
        CheckConstraint("expires_at > created_at", name="ck_watchlist_expiry"),
        Index("ix_watchlist_owner_page", "owner_key", "created_at", "id"),
        Index("ix_watchlist_expiry", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_key: Mapped[str] = mapped_column(String(64), nullable=False)
    pair: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    policy_reference: Mapped[str] = mapped_column(String(200), nullable=False)
