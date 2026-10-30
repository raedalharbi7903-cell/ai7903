"""Owner-scoped snapshots; no customer credentials or raw candle input stored."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AnalysisHistoryRecord(Base):
    __tablename__ = "analysis_history"
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="ck_analysis_history_expiry"),
        Index("ix_analysis_history_owner_page", "owner_key", "created_at", "id"),
        Index("ix_analysis_history_expiry", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_key: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    policy_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)
