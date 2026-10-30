"""Real SQLite persistence/ownership/audit regressions; no market service calls."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.database.base import Base
from app.models.audit import AuditEvent
from app.models.watchlist import WatchlistRecord
from app.schemas.watchlist import WatchlistInput, WatchlistItem, WatchlistQuery
from app.security.identity import VerifiedSession
from app.services.history_mutations import AuditPolicy
from app.services.watchlist import WatchlistPolicy, WatchlistService

NOW = datetime(2026, 10, 30, tzinfo=UTC)
INPUT = WatchlistInput(pair="BTC-USDT", timeframe="1h")


def actor(subject="alice"):
    return VerifiedSession(
        issuer="synthetic-watchlist",
        subject=subject,
        email_verified=True,
        mfa_verified=False,
        expires_at=NOW + timedelta(hours=1),
    )


@pytest.fixture
def engine():
    database = create_engine("sqlite://")
    Base.metadata.create_all(database)
    yield database
    database.dispose()


def service(session, now=NOW, audit=True):
    return WatchlistService(
        session,
        policy=WatchlistPolicy(
            retention_seconds=60, approval_reference="synthetic-only"
        ),
        audit_policy=(
            AuditPolicy(retention_seconds=3600, approval_reference="synthetic-audit")
            if audit
            else None
        ),
        clock=lambda: now,
    )


def counts(engine):
    with Session(engine) as session:
        return (
            session.scalar(select(func.count()).select_from(WatchlistRecord)),
            session.scalar(select(func.count()).select_from(AuditEvent)),
        )


def saved(engine, identity=None, payload=INPUT):
    with Session(engine) as session:
        item, created = service(session).create(identity or actor(), payload)
        assert created
        return item


def test_real_create_duplicate_delete_and_minimal_audit(engine):
    first = saved(engine)
    with Session(engine) as session:
        duplicate, created = service(session).create(actor(), INPUT)
    assert not created
    assert duplicate == first
    assert counts(engine) == (1, 1)
    with Session(engine) as session:
        service(session).delete(actor(), first.id)
    assert counts(engine) == (0, 2)
    with Session(engine) as session:
        events = session.scalars(select(AuditEvent)).all()
        assert {row.action for row in events} == {
            "watchlist.created",
            "watchlist.deleted",
        }
        assert all(row.resource_id == str(first.id) for row in events)
        assert all(
            row.expires_at - row.occurred_at == timedelta(hours=1) for row in events
        )
        assert all(row.owner_key != actor().subject for row in events)
    assert set(WatchlistItem.model_fields) == {
        "id",
        "pair",
        "timeframe",
        "created_at",
        "expires_at",
    }


def test_owners_and_issuers_are_isolated_and_delete_is_non_disclosing(engine):
    item = saved(engine)
    for other in (actor("bob"), actor().model_copy(update={"issuer": "other"})):
        with Session(engine) as session:
            assert service(session).page(other, WatchlistQuery()).items == []
        for identifier in (item.id, uuid4()):
            with Session(engine) as session:
                with pytest.raises(APIError) as failure:
                    service(session).delete(other, identifier)
                assert failure.value.status_code == 404
    assert counts(engine) == (1, 1)


def test_same_pair_can_be_saved_independently_by_two_owners(engine):
    first = saved(engine)
    second = saved(engine, actor("bob"))
    assert first.id != second.id
    assert counts(engine) == (2, 2)


def test_expired_item_hidden_delete_denied_and_explicit_readd_replaces(engine):
    first = saved(engine)
    later = NOW + timedelta(seconds=61)
    with Session(engine) as session:
        assert service(session, later).page(actor(), WatchlistQuery()).items == []
    with Session(engine) as session:
        with pytest.raises(APIError) as failure:
            service(session, later).delete(actor(), first.id)
        assert failure.value.status_code == 404
    with Session(engine) as session:
        second, created = service(session, later).create(actor(), INPUT)
    assert created and second.id != first.id
    assert second.created_at == later
    assert counts(engine) == (1, 2)


def test_keyset_paging_equal_timestamps_is_owner_scoped(engine):
    for name in ("BTC", "ETH", "SOL", "XRP", "LTC"):
        saved(engine, payload=WatchlistInput(pair=name + "-USDT", timeframe="1h"))
    saved(engine, actor("bob"))
    identifiers = []
    cursor = None
    for _ in range(4):
        query = WatchlistQuery(
            limit=2,
            **(
                {"before_created_at": cursor.created_at, "before_id": cursor.id}
                if cursor
                else {}
            ),
        )
        with Session(engine) as session:
            page = service(session).page(actor(), query)
        identifiers.extend(item.id for item in page.items)
        cursor = page.next_cursor
        if cursor is None:
            break
    assert len(identifiers) == len(set(identifiers)) == 5
    assert identifiers == sorted(identifiers, reverse=True)


@pytest.mark.parametrize("operation", ["create", "delete"])
@pytest.mark.parametrize("failure", ["audit", "commit"])
def test_atomic_audit_or_commit_failure_rolls_back_both(
    engine, monkeypatch, operation, failure
):
    item = saved(engine) if operation == "delete" else None
    expected = (1, 1) if item else (0, 0)
    with Session(engine) as session:
        writer = service(session)

        def broken(*args):
            raise SQLAlchemyError("PRIVATE_AUDIT_STORAGE_SECRET")

        if failure == "audit":
            monkeypatch.setattr(writer._audit, "append", broken)
        else:
            event.listen(session, "before_commit", broken)
        try:
            with pytest.raises(SQLAlchemyError):
                if item:
                    writer.delete(actor(), item.id)
                else:
                    writer.create(actor(), INPUT)
        finally:
            if failure == "commit":
                event.remove(session, "before_commit", broken)
    assert counts(engine) == expected


@pytest.mark.parametrize(
    "value",
    [
        {"email_verified": "true"},
        {"mfa_verified": 1},
        {"expires_at": NOW},
        {"issuer": ""},
    ],
)
def test_copied_invalid_or_expired_identity_fails_closed(engine, value):
    invalid = actor().model_copy(update=value)
    with Session(engine) as session:
        with pytest.raises(APIError) as failure:
            service(session).create(invalid, INPUT)
        assert failure.value.status_code == 401
    assert counts(engine) == (0, 0)


def test_mutation_requires_separate_audit_policy(engine):
    with Session(engine) as session:
        with pytest.raises(APIError) as failure:
            service(session, audit=False).create(actor(), INPUT)
        assert failure.value.status_code == 503
    assert counts(engine) == (0, 0)


def test_database_unique_constraint_prevents_duplicate_owner_pair_timeframe(engine):
    item = saved(engine)
    with Session(engine) as session:
        old = session.get(WatchlistRecord, str(item.id))
        session.add(
            WatchlistRecord(
                id=str(uuid4()),
                owner_key=old.owner_key,
                pair=old.pair,
                timeframe=old.timeframe,
                created_at=old.created_at,
                expires_at=old.expires_at,
                policy_reference=old.policy_reference,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    assert counts(engine) == (1, 1)


def test_unrelated_insert_integrity_error_is_not_disguised_as_duplicate(
    engine, monkeypatch
):
    with Session(engine) as session:
        writer = service(session)

        def broken(record):
            raise IntegrityError("synthetic", {}, Exception("private"))

        monkeypatch.setattr(writer._repository, "add", broken)
        with pytest.raises(IntegrityError):
            writer.create(actor(), INPUT)
    assert counts(engine) == (0, 0)


def test_unique_constraint_resolution_returns_existing_without_duplicate_audit(
    engine, monkeypatch
):
    first = saved(engine)
    with Session(engine) as session:
        writer = service(session)
        matching = writer._repository.matching
        calls = []

        def first_read_misses(*args):
            calls.append(True)
            # Simulate the initial read preceding another committed insertion.
            # The insert itself hits the real database unique constraint.
            return None if len(calls) == 1 else matching(*args)

        monkeypatch.setattr(writer._repository, "matching", first_read_misses)
        duplicate, created = writer.create(actor(), INPUT)
    assert len(calls) == 2
    assert duplicate == first and not created
    assert counts(engine) == (1, 1)


def test_session_expiry_during_write_rolls_back_preference_and_audit(
    engine, monkeypatch
):
    clock = [NOW]
    with Session(engine) as session:
        writer = WatchlistService(
            session,
            policy=WatchlistPolicy(
                retention_seconds=60, approval_reference="synthetic-only"
            ),
            audit_policy=AuditPolicy(
                retention_seconds=3600, approval_reference="synthetic-audit"
            ),
            clock=lambda: clock[0],
        )
        add = writer._repository.add

        def expire_after_insert(record):
            add(record)
            clock[0] = NOW + timedelta(hours=2)

        monkeypatch.setattr(writer._repository, "add", expire_after_insert)
        with pytest.raises(APIError) as failure:
            writer.create(actor(), INPUT)
        assert failure.value.status_code == 401
    assert counts(engine) == (0, 0)


@pytest.mark.parametrize(
    "change", [{"pair": "btc-usdt"}, {"timeframe": "fixture"}, {"pair": True}]
)
def test_model_copy_cannot_bypass_preference_validation(engine, change):
    invalid = INPUT.model_copy(update=change)
    with Session(engine) as session:
        with pytest.raises(ValueError):
            service(session).create(actor(), invalid)
    assert counts(engine) == (0, 0)


@pytest.mark.parametrize("race", [False, True])
@pytest.mark.parametrize("expiry", ["identity", "item"])
def test_duplicate_lookup_rechecks_identity_and_item_expiry(
    engine, monkeypatch, race, expiry
):
    saved(engine)
    clock = [NOW]
    with Session(engine) as session:
        writer = WatchlistService(
            session,
            policy=WatchlistPolicy(
                retention_seconds=60, approval_reference="synthetic-only"
            ),
            audit_policy=AuditPolicy(
                retention_seconds=3600, approval_reference="synthetic-audit"
            ),
            clock=lambda: clock[0],
        )
        matching = writer._repository.matching
        calls = []

        def delayed_lookup(*args):
            calls.append(True)
            if race and len(calls) == 1:
                return None
            record = matching(*args)
            clock[0] = NOW + (
                timedelta(hours=2) if expiry == "identity" else timedelta(seconds=61)
            )
            return record

        monkeypatch.setattr(writer._repository, "matching", delayed_lookup)
        with pytest.raises(APIError) as failure:
            writer.create(actor(), INPUT)
        assert failure.value.status_code == (401 if expiry == "identity" else 404)
        assert len(calls) == (2 if race else 1)
    assert counts(engine) == (1, 1)
