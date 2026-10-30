"""Explicitly gated history over the existing analysis pipeline, not a second one."""

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from math import isfinite
from typing import Any
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationError
from pydantic_core import PydanticSerializationError

from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.service import AnalysisService
from app.models.analysis_history import AnalysisHistoryRecord
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.security.identity import VerifiedSession

MAX_RESULT_BYTES = 1024 * 1024
MAX_PAGE_SIZE = 100


class HistoryUnavailableError(Exception):
    """History has no explicitly configured retention policy."""


class HistoryAccessError(Exception):
    """A trusted, current, verified customer session is required."""


class HistoryPolicy(BaseModel):
    """Deployment supplies an approved policy; there is no default duration."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    retention_seconds: int = Field(gt=0)
    approval_reference: str = Field(min_length=1, max_length=200, pattern=r"\S")


class HistoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    id: UUID
    created_at: AwareDatetime
    expires_at: AwareDatetime
    result: AnalysisResult


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
        if not isinstance(identity, VerifiedSession):
            raise HistoryAccessError
        try:
            identity = VerifiedSession.model_validate(
                identity.model_dump(warnings="error")
            )
        except (ValidationError, PydanticSerializationError) as error:
            raise HistoryAccessError from error
        if not identity.email_verified or identity.expires_at <= now:
            raise HistoryAccessError
        if self._policy is None:
            raise HistoryUnavailableError
        principal = json.dumps([identity.issuer, identity.subject], ensure_ascii=False)
        return hashlib.sha256(principal.encode("utf-8")).hexdigest(), now

    @staticmethod
    def _entry(record: AnalysisHistoryRecord) -> HistoryEntry:
        return HistoryEntry(
            id=UUID(record.id),
            created_at=_utc(record.created_at),
            expires_at=_utc(record.expires_at),
            result=AnalysisResult.model_validate_json(record.result_json),
        )

    def record(self, identity: VerifiedSession, result: AnalysisResult) -> HistoryEntry:
        owner, now = self._access(identity)
        # Validate mutated models as well; reject NaN/Infinity before persistence.
        snapshot = AnalysisResult.model_validate(result.model_dump())
        _reject_nonfinite(snapshot.model_dump())
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
        limit: int = 20,
        before: tuple[datetime, UUID] | None = None,
    ) -> list[HistoryEntry]:
        owner, now = self._access(identity)
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
        return [
            self._entry(row) for row in self._repository.list(owner, now, limit, cursor)
        ]

    def delete(self, identity: VerifiedSession, identifier: UUID) -> bool:
        owner, _ = self._access(identity)
        return self._repository.delete(owner, str(identifier))

    def purge_expired(self, identity: VerifiedSession, *, limit: int = 100) -> int:
        owner, now = self._access(identity)
        if type(limit) is not int or not 1 <= limit <= MAX_PAGE_SIZE:
            raise ValueError("Purge size outside storage bound")
        return self._repository.purge_expired(owner, now, limit)
