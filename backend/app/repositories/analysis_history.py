"""All history reads and deletions include an explicit owner predicate."""

from datetime import datetime

from sqlalchemy import and_, delete, or_, select
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

    def list(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> list[AnalysisHistoryRecord]:
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
        return list(
            self._session.scalars(
                statement.order_by(model.created_at.desc(), model.id.desc()).limit(
                    limit
                )
            )
        )

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
