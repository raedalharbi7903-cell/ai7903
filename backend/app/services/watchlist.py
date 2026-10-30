"""Explicit owner-only preferences with atomic minimal audit, no market execution."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import APIError, ResourceNotFoundError
from app.core.retention import RetentionPolicy
from app.models.audit import AuditEvent
from app.models.watchlist import WatchlistRecord
from app.repositories.audit import AuditRepository
from app.repositories.watchlist import WatchlistRepository
from app.schemas.history import HistoryCursor
from app.schemas.watchlist import (
    WatchlistInput,
    WatchlistItem,
    WatchlistPage,
    WatchlistQuery,
)
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
    validate_customer_session,
)
from app.services.history_mutations import AuditPolicy


class WatchlistPolicy(RetentionPolicy):
    """Separate purpose-specific retention; no history-policy borrowing."""


def utc(value: datetime) -> datetime:
    # SQLite returns naive stored UTC values; service clocks must be aware.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class WatchlistService:
    def __init__(
        self,
        session: Session,
        *,
        policy: WatchlistPolicy,
        audit_policy: AuditPolicy | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._session = session
        self._policy = WatchlistPolicy.model_validate(
            policy.model_dump(warnings="error")
        )
        self._audit_policy = (
            AuditPolicy.model_validate(audit_policy.model_dump(warnings="error"))
            if audit_policy is not None
            else None
        )
        self._clock = clock
        self._repository = WatchlistRepository(session)
        self._audit = AuditRepository(session)

    def _access(self, identity: VerifiedSession) -> tuple[str, datetime]:
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Watchlist clock must be timezone aware")
        now = now.astimezone(UTC)
        try:
            actor = validate_customer_session(identity, now)
        except SessionVerificationError as error:
            raise APIError(401, "authentication_required", "Access denied") from error
        return principal_key(actor), now

    @staticmethod
    def _item(record: WatchlistRecord) -> WatchlistItem:
        return WatchlistItem(
            id=UUID(record.id),
            pair=record.pair,
            timeframe=record.timeframe,
            created_at=utc(record.created_at),
            expires_at=utc(record.expires_at),
        )

    def page(self, identity: VerifiedSession, query: WatchlistQuery) -> WatchlistPage:
        owner, now = self._access(identity)
        query = WatchlistQuery.model_validate(query.model_dump(warnings="error"))
        before = (
            (utc(query.before_created_at), str(query.before_id))
            if query.before_created_at is not None
            else None
        )
        records = self._repository.page(owner, now, query.limit, before)
        items = [self._item(record) for record in records]
        cursor = (
            HistoryCursor(created_at=items[-1].created_at, id=items[-1].id)
            if len(items) == query.limit
            else None
        )
        return WatchlistPage(items=items, next_cursor=cursor)

    def _require_audit(self) -> None:
        if self._audit_policy is None:
            raise APIError(
                503, "watchlist_mutation_unavailable", "Watchlist writing unavailable"
            )

    def _existing_item(
        self, identity: VerifiedSession, record: WatchlistRecord
    ) -> WatchlistItem:
        # Database waits can outlive either session or preference validity.
        owner, now = self._access(identity)
        if record.owner_key != owner or utc(record.expires_at) <= now:
            raise ResourceNotFoundError("Watchlist item")
        return self._item(record)

    def _append_audit(
        self, identity: VerifiedSession, resource: UUID, action: str
    ) -> None:
        owner, now = self._access(identity)
        self._audit.append(
            AuditEvent(
                id=str(uuid4()),
                owner_key=owner,
                resource_id=str(resource),
                action=action,
                occurred_at=now,
                expires_at=now
                + timedelta(seconds=self._audit_policy.retention_seconds),
                policy_reference=self._audit_policy.approval_reference,
            )
        )

    def create(
        self, identity: VerifiedSession, payload: WatchlistInput
    ) -> tuple[WatchlistItem, bool]:
        self._require_audit()
        payload = WatchlistInput.model_validate(payload.model_dump(warnings="error"))
        owner, now = self._access(identity)
        with self._session.begin():
            existing = self._repository.matching(
                owner, payload.pair, payload.timeframe, now
            )
            if existing is not None:
                return self._existing_item(identity, existing), False
            self._repository.remove_expired_match(
                owner, payload.pair, payload.timeframe, now
            )
            record = WatchlistRecord(
                id=str(uuid4()),
                owner_key=owner,
                pair=payload.pair,
                timeframe=payload.timeframe,
                created_at=now,
                expires_at=now + timedelta(seconds=self._policy.retention_seconds),
                policy_reference=self._policy.approval_reference,
            )
            try:
                with self._session.begin_nested():
                    self._repository.add(record)
            except IntegrityError:
                # Resolve only a genuine duplicate; unrelated failures propagate.
                existing = self._repository.matching(
                    owner, payload.pair, payload.timeframe, now
                )
                if existing is None:
                    raise
                return self._existing_item(identity, existing), False
            item = self._item(record)
            self._append_audit(identity, item.id, "watchlist.created")
        return item, True

    def delete(self, identity: VerifiedSession, identifier: UUID) -> None:
        self._require_audit()
        owner, now = self._access(identity)
        with self._session.begin():
            if not self._repository.delete(owner, str(identifier), now):
                raise ResourceNotFoundError("Watchlist item")
            self._append_audit(identity, identifier, "watchlist.deleted")
