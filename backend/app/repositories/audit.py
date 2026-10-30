"""Append-only application audit writer, in the caller's transaction."""

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, event: AuditEvent) -> None:
        self._session.add(event)
        self._session.flush()
