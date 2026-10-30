"""Synthetic owner isolation and lifecycle tests; no identity vendor is bypassed."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.analysis.models import AnalysisResult
from app.database.base import Base
from app.models.analysis_history import AnalysisHistoryRecord
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.security.identity import VerifiedSession
from app.services.analysis_history import (
    MAX_RESULT_BYTES,
    AnalysisHistoryService,
    HistoryAccessError,
    HistoryPolicy,
    HistoryUnavailableError,
)
from tests.analysis.test_pipeline import fixture_input

NOW = datetime(2026, 10, 30, tzinfo=UTC)


def identity(subject="alice", issuer="synthetic-issuer", **changes):
    return VerifiedSession(
        **{
            "issuer": issuer,
            "subject": subject,
            "email_verified": True,
            "mfa_verified": False,
            "expires_at": NOW + timedelta(hours=1),
            **changes,
        }
    )


@pytest.fixture
def history():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        clock = [NOW]
        repository = AnalysisHistoryRepository(session)
        service = AnalysisHistoryService(
            repository,
            policy=HistoryPolicy(
                retention_seconds=60, approval_reference="synthetic-test-policy-only"
            ),
            clock=lambda: clock[0],
        )
        yield session, service, clock, repository
    engine.dispose()


def test_default_disabled_has_no_writes_or_pipeline_execution(history, monkeypatch):
    session, _, _, repository = history
    service = AnalysisHistoryService(repository, clock=lambda: NOW)

    def unexpected(*args):
        pytest.fail("Disabled history must not run the pipeline")

    monkeypatch.setattr(
        "app.services.analysis_history.AnalysisService.analyze", unexpected
    )
    with pytest.raises(HistoryUnavailableError):
        service.analyze_and_record(identity(), fixture_input())
    assert session.scalar(select(func.count()).select_from(AnalysisHistoryRecord)) == 0


@pytest.mark.parametrize(
    "actor",
    [
        None,
        {"subject": "alice", "email_verified": True},
        identity(email_verified=False),
        identity(expires_at=NOW),
        identity(expires_at=NOW - timedelta(seconds=1)),
        identity().model_copy(update={"email_verified": "true"}),
        identity().model_copy(update={"issuer": ""}),
    ],
)
def test_all_operations_require_current_trusted_customer_session(history, actor):
    _, service, _, _ = history
    for operation in (
        lambda: service.record(actor, AnalysisResult(status="completed")),
        lambda: service.get(actor, uuid4()),
        lambda: service.list(actor),
        lambda: service.page(actor),
        lambda: service.delete(actor, uuid4()),
        lambda: service.purge_expired(actor),
    ):
        with pytest.raises(HistoryAccessError):
            operation()


def test_existing_pipeline_is_used_and_all_outputs_survive_json_roundtrip(history):
    session, service, _, _ = history
    entry = service.analyze_and_record(identity(), fixture_input())
    session.commit()
    session.expire_all()
    saved = service.get(identity(), entry.id)
    assert saved is not None
    assert len(saved.result.outputs) == 28
    assert saved.result.model_dump() == entry.result.model_dump()
    assert saved.created_at == NOW
    assert saved.expires_at == NOW + timedelta(seconds=60)
    assert saved.created_at.tzinfo is not None
    row = session.get(AnalysisHistoryRecord, str(entry.id))
    assert row.owner_key != identity().subject
    assert len(row.owner_key) == 64
    assert "email" not in row.result_json
    assert row.policy_reference == "synthetic-test-policy-only"


@pytest.mark.parametrize(
    "other", [identity("bob"), identity(issuer="different-issuer")]
)
def test_foreign_owner_cannot_get_list_or_delete(history, other):
    _, service, _, _ = history
    entry = service.record(identity(), AnalysisResult(status="completed"))
    assert service.get(other, entry.id) is None
    assert service.list(other) == []
    assert service.delete(other, entry.id) is False
    assert service.get(identity(), entry.id) is not None


def test_principal_hash_has_unambiguous_issuer_subject_boundaries(history):
    _, service, _, _ = history
    entry = service.record(
        identity("c", issuer="ab"), AnalysisResult(status="completed")
    )
    assert service.get(identity("bc", issuer="a"), entry.id) is None


def test_returned_snapshots_do_not_mutate_storage_or_original_result(history):
    _, service, _, _ = history
    source = AnalysisResult(status="completed")
    entry = service.record(identity(), source)
    source.decision = "buy"
    entry.result.decision = "sell"
    saved = service.get(identity(), entry.id)
    assert saved.result.decision == "insufficient_data"


def test_equal_timestamp_keyset_pages_have_no_duplicates_or_omissions(history):
    _, service, _, _ = history
    ids = [
        service.record(identity(), AnalysisResult(status="completed")).id
        for _ in range(7)
    ]
    seen = []
    cursor = None
    while page := service.list(identity(), limit=2, before=cursor):
        seen.extend(item.id for item in page)
        cursor = (page[-1].created_at, page[-1].id)
    assert seen == sorted(ids, key=str, reverse=True)
    assert len(set(seen)) == 7


@pytest.mark.parametrize("limit", [True, False, 0, -1, 101, 1.5, "20"])
def test_page_size_is_bounded_and_not_coerced(history, limit):
    _, service, _, _ = history
    with pytest.raises(ValueError):
        service.list(identity(), limit=limit)


def test_naive_cursor_and_clock_rejected(history):
    _, service, clock, _ = history
    with pytest.raises(ValueError, match="cursor"):
        service.list(identity(), before=(NOW.replace(tzinfo=None), uuid4()))
    clock[0] = NOW.replace(tzinfo=None)
    with pytest.raises(ValueError, match="clock"):
        service.list(identity())


def test_expiry_boundary_is_excluded_from_all_reads(history):
    _, service, clock, _ = history
    entry = service.record(identity(), AnalysisResult(status="completed"))
    clock[0] = NOW + timedelta(seconds=59)
    assert service.get(identity(), entry.id) is not None
    clock[0] = NOW + timedelta(seconds=60)
    assert service.get(identity(), entry.id) is None
    assert service.list(identity()) == []
    assert service.delete(identity(), entry.id) is True


def test_owner_delete_is_hard_and_idempotent(history):
    session, service, _, _ = history
    entry = service.record(identity(), AnalysisResult(status="completed"))
    assert service.delete(identity(), entry.id) is True
    assert service.delete(identity(), entry.id) is False
    assert session.get(AnalysisHistoryRecord, str(entry.id)) is None


def test_bounded_expiry_purge_never_deletes_foreign_or_unexpired_history(history):
    session, service, clock, _ = history
    for _ in range(3):
        service.record(identity(), AnalysisResult(status="completed"))
    foreign = service.record(identity("bob"), AnalysisResult(status="completed"))
    clock[0] = NOW + timedelta(seconds=30)
    current = service.record(identity(), AnalysisResult(status="completed"))
    clock[0] = NOW + timedelta(seconds=60)
    assert service.purge_expired(identity(), limit=2) == 2
    assert service.purge_expired(identity(), limit=2) == 1
    assert service.purge_expired(identity(), limit=2) == 0
    assert service.get(identity(), current.id) is not None
    assert session.get(AnalysisHistoryRecord, str(foreign.id)) is not None


@pytest.mark.parametrize("limit", [True, 0, 101, "10"])
def test_purge_is_bounded(history, limit):
    _, service, _, _ = history
    with pytest.raises(ValueError):
        service.purge_expired(identity(), limit=limit)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_nested_result_cannot_be_stored(history, value):
    session, service, _, _ = history
    result = AnalysisResult(
        status="completed",
        outputs=[
            {"engine_name": "synthetic", "status": "completed", "data": {"x": value}}
        ],
    )
    with pytest.raises(ValueError):
        service.record(identity(), result)
    assert session.scalar(select(func.count()).select_from(AnalysisHistoryRecord)) == 0


def test_oversize_snapshot_rejected_before_write(history):
    session, service, _, _ = history
    result = AnalysisResult(
        status="completed",
        outputs=[
            {
                "engine_name": "synthetic",
                "status": "completed",
                "data": {"value": "x" * MAX_RESULT_BYTES},
            }
        ],
    )
    with pytest.raises(ValueError, match="storage bound"):
        service.record(identity(), result)
    assert session.scalar(select(func.count()).select_from(AnalysisHistoryRecord)) == 0


def test_repository_does_not_commit_caller_transaction(history):
    session, service, _, _ = history
    entry = service.record(identity(), AnalysisResult(status="completed"))
    session.rollback()
    assert service.get(identity(), entry.id) is None


def test_database_rejects_zero_retention_geometry(history):
    session, _, _, repository = history
    with pytest.raises(IntegrityError):
        repository.add(
            AnalysisHistoryRecord(
                id=str(uuid4()),
                owner_key="a" * 64,
                created_at=NOW,
                expires_at=NOW,
                policy_reference="synthetic-invalid-policy",
                result_json="{}",
            )
        )
    session.rollback()


@pytest.mark.parametrize(
    "values",
    [
        {"retention_seconds": 0, "approval_reference": "test"},
        {"retention_seconds": True, "approval_reference": "test"},
        {"retention_seconds": 60, "approval_reference": ""},
        {"retention_seconds": 60, "approval_reference": "   "},
    ],
)
def test_policy_requires_explicit_valid_duration_and_reference(values):
    with pytest.raises(ValueError):
        HistoryPolicy(**values)


def test_saved_analysis_requires_original_aware_generation_timestamp(history):
    _, service, _, _ = history
    with pytest.raises(ValueError):
        service.record(
            identity(),
            AnalysisResult(status="completed", generated_at=NOW.replace(tzinfo=None)),
        )
