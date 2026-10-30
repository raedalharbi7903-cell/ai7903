"""Every watchlist operation scopes its SQL by the trusted owner."""

from datetime import datetime

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session

from app.models.watchlist import WatchlistRecord


class WatchlistRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def matching(
        self, owner: str, pair: str, timeframe: str, now: datetime
    ) -> WatchlistRecord | None:
        return self._session.scalar(
            select(WatchlistRecord).where(
                WatchlistRecord.owner_key == owner,
                WatchlistRecord.pair == pair,
                WatchlistRecord.timeframe == timeframe,
                WatchlistRecord.expires_at > now,
            )
        )

    def page(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> list[WatchlistRecord]:
        model = WatchlistRecord
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

    def remove_expired_match(
        self, owner: str, pair: str, timeframe: str, now: datetime
    ) -> None:
        self._session.execute(
            delete(WatchlistRecord).where(
                WatchlistRecord.owner_key == owner,
                WatchlistRecord.pair == pair,
                WatchlistRecord.timeframe == timeframe,
                WatchlistRecord.expires_at <= now,
            )
        )

    def add(self, record: WatchlistRecord) -> None:
        self._session.add(record)
        self._session.flush()

    def delete(self, owner: str, identifier: str, now: datetime) -> bool:
        result = self._session.execute(
            delete(WatchlistRecord).where(
                WatchlistRecord.owner_key == owner,
                WatchlistRecord.id == identifier,
                WatchlistRecord.expires_at > now,
            )
        )
        return result.rowcount == 1
