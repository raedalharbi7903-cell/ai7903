"""Explicitly gated history over the existing analysis pipeline, not a second one."""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from math import isfinite
from typing import Any
from uuid import UUID, uuid4

from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.service import AnalysisService
from app.core.exceptions import APIError
from app.core.retention import RetentionPolicy
from app.models.analysis_history import AnalysisHistoryRecord
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.schemas.history import (
    DEFAULT_HISTORY_PAGE_SIZE,
    HistoryCursor,
    HistoryEntry,
    HistoryHeader,
    HistoryPage,
)
from app.schemas.history import (
    MAX_HISTORY_PAGE_SIZE as MAX_PAGE_SIZE,
)
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
    validate_customer_session,
)

MAX_RESULT_BYTES = 1024 * 1024


class HistoryUnavailableError(APIError):
    """History has no explicitly configured retention policy."""

    def __init__(self) -> None:
        super().__init__(503, "history_unavailable", "Analysis history is unavailable")


class HistoryAccessError(APIError):
    """A trusted, current, verified customer session is required."""

    def __init__(self) -> None:
        super().__init__(401, "authentication_required", "Access denied")


class HistoryPolicy(RetentionPolicy):
    """Deployment supplies an approved policy; there is no default duration."""


def _utc(value: datetime) -> datetime:
    # SQLite drops zone metadata; this private column is always written as UTC.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _reject_nonfinite(value: Any) -> None:
    # Pydantic's JSON mode can turn NaN/Infinity into null. Check before that
    # conversion so an invalid analytical value is not silently sanitized.
    if isinstance(value, float | Decimal) and not isfinite(value):
        raise ValueError("Analysis history snapshot contains a nonfinite value")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_nonfinite(key)
            _reject_nonfinite(item)
    elif isinstance(value, list | tuple | set | frozenset):
        for item in value:
            _reject_nonfinite(item)


def _validated_result(value: object) -> AnalysisResult:
    result = AnalysisResult.model_validate(value)
    if result.generated_at.tzinfo is None or result.generated_at.utcoffset() is None:
        raise ValueError("Saved analysis generation time must be timezone aware")
    _reject_nonfinite(result.model_dump())
    return result


class AnalysisHistoryService:
    def __init__(
        self,
        repository: AnalysisHistoryRepository,
        *,
        policy: HistoryPolicy | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._repository = repository
        self._policy = (
            HistoryPolicy.model_validate(policy.model_dump(warnings="error"))
            if policy is not None
            else None
        )
        self._clock = clock

    def _access(self, identity: VerifiedSession) -> tuple[str, datetime]:
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("History clock must be timezone aware")
        now = now.astimezone(UTC)
        try:
            identity = validate_customer_session(identity, now)
        except SessionVerificationError as error:
            raise HistoryAccessError from error
        if self._policy is None:
            raise HistoryUnavailableError
        return principal_key(identity), now

    @staticmethod
    def _entry(record: AnalysisHistoryRecord) -> HistoryEntry:
        raw = json.loads(record.result_json)
        if (
            not isinstance(raw, dict)
            or not AnalysisResult.model_fields.keys() <= raw.keys()
        ):
            raise ValueError("Stored analysis snapshot is incomplete")
        return HistoryEntry(
            id=UUID(record.id),
            created_at=_utc(record.created_at),
            expires_at=_utc(record.expires_at),
            result=_validated_result(raw),
        )

    def record(self, identity: VerifiedSession, result: AnalysisResult) -> HistoryEntry:
        owner, now = self._access(identity)
        # Validate mutated models as well; reject NaN/Infinity before persistence.
        snapshot = _validated_result(result.model_dump())
        encoded = json.dumps(
            snapshot.model_dump(mode="json"), ensure_ascii=False, allow_nan=False
        )
        if len(encoded.encode("utf-8")) > MAX_RESULT_BYTES:
            raise ValueError("Analysis history snapshot exceeds storage bound")
        assert self._policy is not None
        record = AnalysisHistoryRecord(
            id=str(uuid4()),
            owner_key=owner,
            created_at=now,
            expires_at=now + timedelta(seconds=self._policy.retention_seconds),
            policy_reference=self._policy.approval_reference,
            result_json=encoded,
        )
        self._repository.add(record)
        return self._entry(record)

    def analyze_and_record(
        self, identity: VerifiedSession, payload: AnalysisInput
    ) -> HistoryEntry:
        self._access(identity)
        return self.record(identity, AnalysisService().analyze(payload))

    def get(self, identity: VerifiedSession, identifier: UUID) -> HistoryEntry | None:
        owner, now = self._access(identity)
        record = self._repository.get(owner, str(identifier), now)
        return self._entry(record) if record is not None else None

    def list(
        self,
        identity: VerifiedSession,
        *,
        limit: int = DEFAULT_HISTORY_PAGE_SIZE,
        before: tuple[datetime, UUID] | None = None,
    ) -> list[HistoryEntry]:
        owner, now = self._access(identity)
        cursor = self._page_cursor(limit, before)
        return [
            self._entry(row) for row in self._repository.list(owner, now, limit, cursor)
        ]

    @staticmethod
    def _page_cursor(
        limit: int, before: tuple[datetime, UUID] | None
    ) -> tuple[datetime, str] | None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("Page size must be an integer")
        if not 1 <= limit <= MAX_PAGE_SIZE:
            raise ValueError("Page size outside storage bound")
        cursor = None
        if before is not None:
            timestamp, identifier = before
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("History cursor must be timezone aware")
            cursor = (timestamp.astimezone(UTC), str(identifier))
        return cursor

    def page(
        self,
        identity: VerifiedSession,
        *,
        limit: int = DEFAULT_HISTORY_PAGE_SIZE,
        before: tuple[datetime, UUID] | None = None,
    ) -> HistoryPage:
        owner, now = self._access(identity)
        cursor = self._page_cursor(limit, before)
        items = [
            HistoryHeader(
                id=UUID(identifier), created_at=_utc(created), expires_at=_utc(expires)
            )
            for identifier, created, expires in self._repository.list_headers(
                owner, now, limit, cursor
            )
        ]
        return HistoryPage(
            items=items,
            next_cursor=(
                HistoryCursor(created_at=items[-1].created_at, id=items[-1].id)
                if len(items) == limit
                else None
            ),
        )

    def delete(self, identity: VerifiedSession, identifier: UUID) -> bool:
        owner, _ = self._access(identity)
        return self._repository.delete(owner, str(identifier))

    def purge_expired(
        self, identity: VerifiedSession, *, limit: int = MAX_PAGE_SIZE
    ) -> int:
        owner, now = self._access(identity)
        if type(limit) is not int or not 1 <= limit <= MAX_PAGE_SIZE:
            raise ValueError("Purge size outside storage bound")
        return self._repository.purge_expired(owner, now, limit)
