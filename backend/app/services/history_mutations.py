"""Explicit atomic history mutations; audit failure rolls back the data change."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.analysis.models import AnalysisInput
from app.core.exceptions import ResourceNotFoundError
from app.core.retention import RetentionPolicy
from app.models.audit import AuditEvent
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.repositories.audit import AuditRepository
from app.schemas.history import HistoryEntry
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
    validate_customer_session,
)
from app.services.analysis_history import (
    AnalysisHistoryService,
    HistoryAccessError,
    HistoryPolicy,
)


class AuditPolicy(RetentionPolicy):
    """Separate approved audit retention, never borrowed from result retention."""


class HistoryMutationService:
    """Own a fresh request session transaction; do not nest in caller transactions."""

    def __init__(
        self,
        session: Session,
        *,
        history_policy: HistoryPolicy,
        audit_policy: AuditPolicy,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._session = session
        self._clock = clock
        self._audit_policy = AuditPolicy.model_validate(
            audit_policy.model_dump(warnings="error")
        )
        self._history = AnalysisHistoryService(
            AnalysisHistoryRepository(session), policy=history_policy, clock=clock
        )
        self._audit = AuditRepository(session)

    def _append_audit(
        self,
        identity: VerifiedSession,
        resource: UUID,
        action: str,
    ) -> None:
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Audit clock must be timezone aware")
        now = now.astimezone(UTC)
        try:
            actor = validate_customer_session(identity, now)
        except SessionVerificationError as error:
            raise HistoryAccessError from error
        identifier = str(uuid4())
        self._audit.append(
            AuditEvent(
                id=identifier,
                owner_key=principal_key(actor),
                action=action,
                resource_id=str(resource),
                occurred_at=now,
                expires_at=now
                + timedelta(seconds=self._audit_policy.retention_seconds),
                policy_reference=self._audit_policy.approval_reference,
            )
        )

    def create(self, identity: VerifiedSession, payload: AnalysisInput) -> HistoryEntry:
        with self._session.begin():
            entry = self._history.analyze_and_record(identity, payload)
            self._append_audit(identity, entry.id, "analysis_history.created")
        return entry

    def delete(self, identity: VerifiedSession, identifier: UUID) -> None:
        with self._session.begin():
            if not self._history.delete(identity, identifier):
                raise ResourceNotFoundError("Analysis history")
            self._append_audit(identity, identifier, "analysis_history.deleted")
