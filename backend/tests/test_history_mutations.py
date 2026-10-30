"""Atomic real-DB audit/data behavior, never a mocked successful write."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.database.base import Base
from app.models.analysis_history import AnalysisHistoryRecord
from app.models.audit import AuditEvent
from app.security.identity import VerifiedSession, principal_key
from app.services.analysis_history import HistoryAccessError, HistoryPolicy
from app.services.history_mutations import AuditPolicy, HistoryMutationService
from tests.analysis.test_pipeline import fixture_input

NOW = datetime(2026, 10, 30, tzinfo=UTC)


def actor(subject="alice", **changes):
    return VerifiedSession(
        issuer="synthetic-mutation",
        subject=subject,
        email_verified=True,
        mfa_verified=False,
        expires_at=NOW + timedelta(hours=1),
        **changes,
    )


@pytest.fixture
def store():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def service(session):
    return HistoryMutationService(
        session,
        history_policy=HistoryPolicy(
            retention_seconds=60, approval_reference="synthetic-history-policy"
        ),
        audit_policy=AuditPolicy(
            retention_seconds=3600, approval_reference="synthetic-audit-policy"
        ),
        clock=lambda: NOW,
    )


def counts(engine):
    with Session(engine) as reader:
        return (
            reader.scalar(select(func.count()).select_from(AnalysisHistoryRecord)),
            reader.scalar(select(func.count()).select_from(AuditEvent)),
        )


def saved(engine):
    with Session(engine) as session:
        return service(session).create(actor(), fixture_input())


def test_create_commits_snapshot_and_separate_minimal_audit_together(store):
    entry = saved(store)
    assert counts(store) == (1, 1)
    with Session(store) as session:
        row = session.scalar(select(AuditEvent))
        assert row.resource_id == str(entry.id)
        assert row.owner_key == principal_key(actor())
        assert row.action == "analysis_history.created"
        assert row.policy_reference == "synthetic-audit-policy"
        assert row.expires_at - row.occurred_at == timedelta(seconds=3600)
        history = session.get(AnalysisHistoryRecord, str(entry.id))
        assert history.expires_at - history.created_at == timedelta(seconds=60)
        assert row.owner_key != actor().subject
        assert not hasattr(row, "payload")
        assert len(entry.result.outputs) == 28


def test_delete_commits_erasure_and_audit_together(store):
    entry = saved(store)
    with Session(store) as session:
        service(session).delete(actor(), entry.id)
    assert counts(store) == (0, 2)
    with Session(store) as session:
        actions = session.scalars(select(AuditEvent.action)).all()
        assert set(actions) == {"analysis_history.created", "analysis_history.deleted"}


@pytest.mark.parametrize("operation", ["create", "delete"])
@pytest.mark.parametrize("failure", ["audit", "commit"])
def test_failure_rolls_back_both_sides(store, monkeypatch, operation, failure):
    original = saved(store) if operation == "delete" else None
    expected = (1, 1) if operation == "delete" else (0, 0)
    with Session(store) as session:
        writer = service(session)

        def broken(*args):
            raise SQLAlchemyError("PRIVATE_AUDIT_STORAGE_SECRET")

        if failure == "audit":
            monkeypatch.setattr(writer._audit, "append", broken)
        else:
            event.listen(session, "before_commit", broken)
        try:
            with pytest.raises(SQLAlchemyError):
                if operation == "create":
                    writer.create(actor(), fixture_input())
                else:
                    writer.delete(actor(), original.id)
        finally:
            if failure == "commit":
                event.remove(session, "before_commit", broken)
    assert counts(store) == expected


@pytest.mark.parametrize("foreign", [True, False])
def test_unowned_or_missing_deletion_does_not_create_an_audit(store, foreign):
    entry = saved(store)
    with Session(store) as session:
        with pytest.raises(ResourceNotFoundError):
            service(session).delete(actor("bob"), entry.id if foreign else uuid4())
    assert counts(store) == (1, 1)


@pytest.mark.parametrize("operation", ["create", "delete"])
def test_malformed_or_expired_identity_cannot_mutate(store, operation):
    entry = saved(store)
    for invalid in (
        actor().model_copy(update={"mfa_verified": "true"}),
        actor().model_copy(update={"expires_at": NOW}),
    ):
        with Session(store) as session:
            with pytest.raises(HistoryAccessError):
                if operation == "create":
                    service(session).create(invalid, fixture_input())
                else:
                    service(session).delete(invalid, entry.id)
    assert counts(store) == (1, 1)


def test_expiry_during_analysis_rolls_back_without_snapshot_or_audit(
    store, monkeypatch
):
    clock = [NOW]
    from app.analysis.service import AnalysisService

    original = AnalysisService.analyze

    def analyze_then_expire(self, payload):
        result = original(self, payload)
        clock[0] = NOW + timedelta(hours=2)
        return result

    monkeypatch.setattr(AnalysisService, "analyze", analyze_then_expire)
    with Session(store) as session:
        writer = HistoryMutationService(
            session,
            history_policy=HistoryPolicy(
                retention_seconds=60, approval_reference="synthetic-only"
            ),
            audit_policy=AuditPolicy(
                retention_seconds=3600, approval_reference="synthetic-audit-only"
            ),
            clock=lambda: clock[0],
        )
        with pytest.raises(HistoryAccessError) as caught:
            writer.create(actor(), fixture_input())
        assert caught.value.status_code == 401
    assert counts(store) == (0, 0)


def test_repeated_delete_has_no_duplicate_success_audit(store):
    entry = saved(store)
    with Session(store) as session:
        service(session).delete(actor(), entry.id)
    with Session(store) as session:
        with pytest.raises(ResourceNotFoundError):
            service(session).delete(actor(), entry.id)
    assert counts(store) == (0, 2)
