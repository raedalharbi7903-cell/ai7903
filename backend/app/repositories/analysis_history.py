"""All history reads and deletions include an explicit owner predicate."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, delete, or_, select
from sqlalchemy.orm import Session

from app.models.analysis_history import AnalysisHistoryRecord


class AnalysisHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: AnalysisHistoryRecord) -> None:
        self._session.add(record)
        self._session.flush()

    def get(
        self, owner: str, identifier: str, now: datetime
    ) -> AnalysisHistoryRecord | None:
        return self._session.scalar(
            select(AnalysisHistoryRecord).where(
                AnalysisHistoryRecord.owner_key == owner,
                AnalysisHistoryRecord.id == identifier,
                AnalysisHistoryRecord.expires_at > now,
            )
        )

    def _page(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> Select[tuple[AnalysisHistoryRecord]]:
        model = AnalysisHistoryRecord
        statement = select(model).where(
            model.owner_key == owner, model.expires_at > now
        )
        if before is not None:
            timestamp, identifier = before
            statement = statement.where(
                or_(
                    model.created_at < timestamp,
                    and_(model.created_at == timestamp, model.id < identifier),
                )
            )
        return statement.order_by(model.created_at.desc(), model.id.desc()).limit(limit)

    def list(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> list[AnalysisHistoryRecord]:
        return list(self._session.scalars(self._page(owner, now, limit, before)))

    def list_headers(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> list[tuple[str, datetime, datetime]]:
        model = AnalysisHistoryRecord
        statement = self._page(owner, now, limit, before).with_only_columns(
            model.id, model.created_at, model.expires_at
        )
        return [
            (row.id, row.created_at, row.expires_at)
            for row in self._session.execute(statement)
        ]

    def delete(self, owner: str, identifier: str) -> bool:
        result = self._session.execute(
            delete(AnalysisHistoryRecord).where(
                AnalysisHistoryRecord.owner_key == owner,
                AnalysisHistoryRecord.id == identifier,
            )
        )
        return result.rowcount == 1

    def purge_expired(self, owner: str, now: datetime, limit: int) -> int:
        model = AnalysisHistoryRecord
        expired = (
            select(model.id)
            .where(model.owner_key == owner, model.expires_at <= now)
            .order_by(model.expires_at, model.id)
            .limit(limit)
        )
        result = self._session.execute(
            delete(model).where(model.owner_key == owner, model.id.in_(expired))
        )
        return result.rowcount
