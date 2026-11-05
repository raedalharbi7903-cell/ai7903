"""Owner-scoped billing queries and locked normalized-event lookup; no commits."""

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.billing import BillingEventRecord, SubscriptionRecord


class BillingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def subscription(
        self, owner: str, *, lock: bool = False
    ) -> SubscriptionRecord | None:
        query = select(SubscriptionRecord).where(SubscriptionRecord.owner_key == owner)
        if lock:
            query = query.with_for_update()
        return self._session.scalar(query)

    def event(self, provider: str, event_id: str) -> BillingEventRecord | None:
        return self._session.scalar(
            select(BillingEventRecord)
            .where(
                BillingEventRecord.provider == provider,
                BillingEventRecord.provider_event_id == event_id,
            )
            .with_for_update()
        )

    def add(self, record: SubscriptionRecord | BillingEventRecord) -> None:
        self._session.add(record)
        self._session.flush()

    def history(
        self,
        owner: str,
        now: datetime,
        limit: int,
        before: tuple[datetime, str] | None,
    ) -> list[BillingEventRecord]:
        model = BillingEventRecord
        query = select(model).where(
            model.owner_key == owner, model.retained_until > now
        )
        if before:
            stamp, identifier = before
            query = query.where(
                or_(
                    model.recorded_at < stamp,
                    and_(model.recorded_at == stamp, model.id < identifier),
                )
            )
        return list(
            self._session.scalars(
                query.order_by(model.recorded_at.desc(), model.id.desc()).limit(limit)
            )
        )
