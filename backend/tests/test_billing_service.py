"""Real SQLite billing tests; all events and policies are synthetic, not a gateway."""

import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.exceptions import APIError
from app.database.base import Base
from app.models.audit import AuditEvent
from app.models.billing import BillingEventRecord, SubscriptionRecord
from app.schemas.billing import (
    BillingHistoryItem,
    BillingHistoryQuery,
    VerifiedBillingEvent,
)
from app.security.identity import VerifiedSession, principal_key
from app.services.billing import BillingPolicy, BillingService
from app.services.history_mutations import AuditPolicy
from tests.test_migration_recovery import migrate

NOW = datetime(2026, 11, 5, tzinfo=UTC)
END = datetime(2026, 12, 5, tzinfo=UTC)


def actor(subject="alice", expires_at=NOW + timedelta(days=200)):
    return VerifiedSession(
        issuer="synthetic-billing",
        subject=subject,
        email_verified=True,
        mfa_verified=False,
        expires_at=expires_at,
    )


def paid(**changes):
    return VerifiedBillingEvent(
        **{
            "provider": "synthetic",
            "event_id": "event-1",
            "owner_key": principal_key(actor()),
            "kind": "paid",
            "occurred_at": NOW,
            "paid_period_start": NOW,
            "paid_period_end": END,
            "amount_minor": 12345,
            "currency": "SAR",
            "renewal_consent": True,
            "consent_reference": "synthetic-consent-not-real-approval",
            **changes,
        }
    )


@pytest.fixture
def engine():
    database = create_engine("sqlite://")
    Base.metadata.create_all(database)
    yield database
    database.dispose()


def service(session, now=NOW, *, policy=True, audit=True):
    return BillingService(
        session,
        policy=(
            BillingPolicy(
                retention_seconds=86400 * 365,
                approval_reference="synthetic-retention-not-legal-policy",
            )
            if policy
            else None
        ),
        audit_policy=(
            AuditPolicy(retention_seconds=86400, approval_reference="synthetic-audit")
            if audit
            else None
        ),
        clock=lambda: now,
    )


def process(engine, payload=None, now=NOW):
    with Session(engine) as session:
        return service(session, now).process_event(payload or paid())


def summary(engine, identity=None, now=NOW):
    with Session(engine) as session:
        return service(session, now).summary(identity or actor())


def counts(engine):
    with Session(engine) as session:
        return tuple(
            session.scalar(select(func.count()).select_from(model))
            for model in (SubscriptionRecord, BillingEventRecord, AuditEvent)
        )


def test_unpaid_summary_never_creates_trial_account_or_access(engine):
    result = summary(engine)
    assert result.state == "none" and not result.entitled
    assert result.plan == "monthly" and result.paid_period_end is None
    assert counts(engine) == (0, 0, 0)


def test_paid_access_has_exact_start_and_expiry_without_grace(engine):
    result = process(engine)
    assert result.processing_status == "applied" and not result.duplicate
    assert summary(engine, now=NOW - timedelta(microseconds=1)).state == "scheduled"
    assert not summary(engine, now=NOW - timedelta(microseconds=1)).entitled
    assert summary(engine, now=NOW).entitled
    assert summary(engine, now=END - timedelta(microseconds=1)).entitled
    expired = summary(engine, now=END)
    assert expired.state == "expired" and not expired.entitled
    assert (expired.paid_period_start, expired.paid_period_end) == (NOW, END)
    assert counts(engine) == (1, 1, 1)


def test_owner_isolation_includes_issuer_and_cancellation(engine):
    process(engine)
    assert summary(engine, actor("bob")).state == "none"
    assert (
        summary(engine, actor().model_copy(update={"issuer": "other"})).state == "none"
    )
    with Session(engine) as session:
        with pytest.raises(APIError) as denied:
            service(session).cancel(actor("bob"))
        assert denied.value.status_code == 404
    assert summary(engine).entitled
    assert counts(engine) == (1, 1, 1)


def test_cancel_is_idempotent_and_keeps_access_until_original_paid_end(engine):
    process(engine)
    for _ in range(2):
        with Session(engine) as session:
            result = service(session).cancel(actor())
        assert result.cancel_at_period_end and result.entitled
        assert not result.renewal_consent and result.paid_period_end == END
        assert counts(engine) == (1, 1, 2)
    assert not summary(engine, now=END).entitled


def test_consented_contiguous_renewal_preserves_current_paid_access(engine):
    process(engine)
    later = datetime(2027, 1, 5, tzinfo=UTC)
    process(
        engine, paid(event_id="renewal", paid_period_start=END, paid_period_end=later)
    )
    result = summary(engine)
    assert result.entitled
    assert (result.paid_period_start, result.paid_period_end) == (NOW, later)
    assert counts(engine) == (1, 2, 2)


@pytest.mark.parametrize("cancelled", [False, True])
def test_renewal_without_standing_consent_or_after_cancel_is_review_only(
    engine, cancelled
):
    process(engine, paid(renewal_consent=False, consent_reference=None))
    if cancelled:
        with Session(engine) as session:
            service(session).cancel(actor())
    receipt = process(
        engine,
        paid(
            event_id="new",
            paid_period_start=END,
            paid_period_end=datetime(2027, 1, 5, tzinfo=UTC),
        ),
    )
    assert receipt.processing_status == "review_required"
    result = summary(engine)
    assert result.review_required and result.entitled
    assert (result.paid_period_start, result.paid_period_end) == (NOW, END)
    assert not result.renewal_consent


def test_failed_payment_never_grants_or_shortens_paid_window(engine):
    failure = paid(kind="payment_failed", event_id="failed")
    process(engine, failure)
    assert summary(engine).state == "none"
    assert counts(engine) == (0, 1, 1)
    process(engine)
    process(engine, failure.model_copy(update={"event_id": "failed-again"}))
    result = summary(engine)
    assert result.entitled and not result.review_required
    assert result.paid_period_end == END
    assert counts(engine) == (1, 3, 3)


@pytest.mark.parametrize("kind", ["refund", "dispute", "unsupported"])
def test_unsupported_financial_outcomes_do_not_invent_refund_policy(engine, kind):
    process(engine)
    receipt = process(engine, paid(event_id="review", kind=kind))
    assert receipt.processing_status == "review_required"
    result = summary(engine)
    assert result.state == "review_required" and result.entitled
    assert (result.paid_period_start, result.paid_period_end) == (NOW, END)


@pytest.mark.parametrize(
    "kind", ["paid", "payment_failed", "refund", "dispute", "unsupported"]
)
def test_any_future_financial_event_is_quarantined_not_normal_applied(engine, kind):
    receipt = process(engine, paid(kind=kind, occurred_at=NOW + timedelta(seconds=1)))
    assert receipt.processing_status == "review_required"
    assert not summary(engine).entitled
    assert summary(engine).paid_period_end is None


@pytest.mark.parametrize(
    "changes",
    [
        {"paid_period_start": NOW - timedelta(days=31), "paid_period_end": NOW},
        {
            "paid_period_start": END - timedelta(days=1),
            "paid_period_end": END + timedelta(days=30),
        },
        {
            "paid_period_start": END + timedelta(days=1),
            "paid_period_end": END + timedelta(days=31),
        },
    ],
)
def test_backward_overlapping_or_disjoint_future_period_never_replaces_paid_window(
    engine, changes
):
    process(engine)
    receipt = process(engine, paid(event_id="bad-window", **changes))
    assert receipt.processing_status == "review_required"
    assert (summary(engine).paid_period_start, summary(engine).paid_period_end) == (
        NOW,
        END,
    )


def test_identical_replay_is_durable_and_cannot_regrant_expired_access(engine):
    first = process(engine)
    repeated = process(engine, now=END + timedelta(days=1))
    assert repeated.id == first.id and repeated.duplicate
    assert not summary(engine, now=END + timedelta(days=1)).entitled
    assert counts(engine) == (1, 1, 1)


def test_conflicting_event_key_cannot_change_owner_amount_or_granted_window(engine):
    original = process(engine)
    conflict = paid(owner_key=principal_key(actor("bob")), amount_minor=99999)
    for _ in range(2):
        receipt = process(engine, conflict)
        assert receipt.id == original.id
        assert receipt.processing_status == "review_required"
    assert summary(engine, actor("bob")).state == "none"
    assert summary(engine).review_required and summary(engine).paid_period_end == END
    assert counts(engine) == (1, 1, 2)
    with Session(engine) as session:
        record = session.scalar(select(BillingEventRecord))
        assert (
            record.owner_key == principal_key(actor()) and record.amount_minor == 12345
        )


def test_provider_is_part_of_event_identity(engine):
    process(engine)
    process(engine, paid(provider="other", kind="payment_failed"))
    assert counts(engine) == (1, 2, 2)


@pytest.mark.parametrize("operation", ["event", "cancel"])
@pytest.mark.parametrize("failure", ["audit", "commit"])
def test_mutation_and_audit_always_roll_back_together(
    engine, monkeypatch, operation, failure
):
    if operation == "cancel":
        process(engine)
    before = counts(engine)
    with Session(engine) as session:
        writer = service(session)

        def broken(*args):
            raise SQLAlchemyError("PRIVATE_BILLING_AUDIT_SECRET")

        if failure == "audit":
            monkeypatch.setattr(writer._audit, "append", broken)
        else:
            sqlalchemy_event.listen(session, "before_commit", broken)
        try:
            with pytest.raises(SQLAlchemyError):
                (
                    writer.process_event(paid())
                    if operation == "event"
                    else writer.cancel(actor())
                )
        finally:
            if failure == "commit":
                sqlalchemy_event.remove(session, "before_commit", broken)
    assert counts(engine) == before
    if operation == "cancel":
        assert not summary(engine).cancel_at_period_end


def test_actual_unique_constraint_race_returns_safe_retry_then_duplicate(
    engine, monkeypatch
):
    process(engine)
    with Session(engine) as session:
        writer = service(session)
        monkeypatch.setattr(writer._repository, "event", lambda *_: None)
        with pytest.raises(APIError) as conflict:
            writer.process_event(paid())
        assert conflict.value.status_code == 409
        assert conflict.value.code == "billing_retry_required"
    assert counts(engine) == (1, 1, 1)
    assert process(engine).duplicate


def test_actual_optimistic_version_prevents_stale_writes(engine):
    process(engine)
    with Session(engine) as first, Session(engine) as second:
        one = first.scalar(select(SubscriptionRecord))
        two = second.scalar(select(SubscriptionRecord))
        one.cancel_at_period_end = True
        one.renewal_consent = False
        first.commit()
        two.review_required = True
        with pytest.raises(StaleDataError):
            second.commit()
    assert summary(engine).cancel_at_period_end
    assert not summary(engine).review_required


def test_unrelated_integrity_error_is_not_hidden_as_retry(engine, monkeypatch):
    with Session(engine) as session:
        writer = service(session)
        append = writer._audit.append

        def invalid(row):
            row.expires_at = row.occurred_at
            append(row)

        monkeypatch.setattr(writer._audit, "append", invalid)
        with pytest.raises(IntegrityError):
            writer.process_event(paid())
    assert counts(engine) == (0, 0, 0)


@pytest.mark.parametrize(
    "field,value",
    [("email_verified", "true"), ("mfa_verified", 1), ("expires_at", NOW)],
)
def test_copied_customer_claims_and_expiry_do_not_authenticate(engine, field, value):
    with Session(engine) as session:
        with pytest.raises(APIError) as denied:
            service(session).summary(actor().model_copy(update={field: value}))
        assert denied.value.status_code == 401


def test_session_expiry_while_waiting_for_cancel_lock_rolls_back(engine, monkeypatch):
    process(engine)
    clock = [NOW]
    with Session(engine) as session:
        writer = service(session)
        writer._clock = lambda: clock[0]
        original = writer._repository.subscription

        def slow(*args, **kwargs):
            record = original(*args, **kwargs)
            clock[0] = NOW + timedelta(seconds=2)
            return record

        monkeypatch.setattr(writer._repository, "subscription", slow)
        with pytest.raises(APIError) as denied:
            writer.cancel(actor(expires_at=NOW + timedelta(seconds=1)))
        assert denied.value.status_code == 401
    assert counts(engine) == (1, 1, 1)
    assert not summary(engine).cancel_at_period_end


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount_minor", True),
        ("amount_minor", 12.5),
        ("renewal_consent", "true"),
        ("paid_period_end", NOW),
        ("plan", "annual"),
    ],
)
def test_constructed_event_model_is_revalidated_not_signature_proof(
    engine, field, value
):
    with Session(engine) as session:
        with pytest.raises(ValueError):
            service(session).process_event(paid().model_copy(update={field: value}))
    assert counts(engine) == (0, 0, 0)


@pytest.mark.parametrize(
    "changes",
    [
        {"plan": "annual"},
        {"plan": "trial"},
        {"amount_minor": 0},
        {"amount_minor": -1},
        {"amount_minor": True},
        {"amount_minor": 9223372036854775808},
        {"amount_minor": 1.5},
        {"currency": "sar"},
        {"currency": None},
        {"owner_key": "client-owner"},
        {"paid_period_start": NOW.replace(tzinfo=None)},
        {"paid_period_end": NOW},
        {"occurred_at": NOW.astimezone(timezone(timedelta(hours=3)))},
        {"renewal_consent": True, "consent_reference": None},
    ],
)
def test_invalid_money_tier_period_and_consent_are_not_coerced(changes):
    with pytest.raises(ValidationError):
        paid(**changes)


def test_no_default_policy_or_implicit_audit_policy(engine):
    with Session(engine) as session:
        with pytest.raises(APIError) as denied:
            BillingService(session).summary(actor())
        assert denied.value.status_code == 503
        with pytest.raises(APIError) as denied:
            service(session, audit=False).process_event(paid())
        assert denied.value.status_code == 503
    assert counts(engine) == (0, 0, 0)


def test_public_history_is_lossless_minimal_owned_and_keyset_paginated(engine):
    process(engine, paid(amount_minor=9223372036854775807))
    for index in range(3):
        process(engine, paid(event_id=f"failed-{index}", kind="payment_failed"))
    process(engine, paid(event_id="bob", owner_key=principal_key(actor("bob"))))
    with Session(engine) as session:
        first = service(session).history(actor(), BillingHistoryQuery(limit=2))
    with Session(engine) as session:
        following = service(session).history(
            actor(),
            BillingHistoryQuery(
                limit=2,
                before_created_at=first.next_cursor.created_at,
                before_id=first.next_cursor.id,
            ),
        )
    items = first.items + following.items
    assert len(items) == len({item.id for item in items}) == 4
    assert any(item.amount_minor == "9223372036854775807" for item in items)
    expected = {
        "id",
        "kind",
        "amount_minor",
        "currency",
        "recorded_at",
        "retained_until",
        "processing_status",
    }
    assert all(set(item.model_dump()) == expected for item in items)
    assert all(
        secret not in first.model_dump_json()
        for secret in ("owner_key", "fingerprint", "provider_event_id")
    )


def test_visibility_expiry_never_deletes_ledger_or_breaks_idempotency(engine):
    process(engine)
    late = END + timedelta(days=366)
    with Session(engine) as session:
        page = service(session, late).history(
            actor(expires_at=late + timedelta(days=1)), BillingHistoryQuery()
        )
        assert page.items == []
    assert process(engine, now=late).duplicate
    assert counts(engine) == (1, 1, 1)


def test_unknown_owner_filters_and_copied_invalid_history_query_are_rejected(engine):
    with pytest.raises(ValidationError):
        BillingHistoryQuery(owner_key=principal_key(actor()))
    with Session(engine) as session:
        with pytest.raises(ValueError):
            service(session).history(
                actor(), BillingHistoryQuery().model_copy(update={"limit": True})
            )


def test_public_minor_units_are_canonical_lossless_strings_not_numbers():
    template = dict(
        id=uuid4(),
        kind="paid",
        amount_minor="9223372036854775807",
        currency="SAR",
        recorded_at=NOW,
        retained_until=END,
        processing_status="applied",
    )
    assert BillingHistoryItem(**template).amount_minor == "9223372036854775807"
    for value in (123, "00123", "1.23", "9223372036854775808"):
        with pytest.raises(ValidationError):
            BillingHistoryItem(**{**template, "amount_minor": value})


def test_schema_migration_preserves_watchlist_and_downgrade_only_removes_billing(
    tmp_path,
):
    path = tmp_path / "synthetic-billing-migration.db"
    first = migrate(path, "upgrade", "20261030_0004")
    assert first.returncode == 0, first.stderr
    identifier = str(uuid4())
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO watchlist VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                identifier,
                principal_key(actor()),
                "BTC-USDT",
                "1h",
                "2026-11-05 00:00:00",
                "2026-12-05 00:00:00",
                "synthetic-policy",
            ),
        )
    upgraded = migrate(path, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stderr
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone() == ("20261105_0005",)
        assert connection.execute("SELECT id FROM watchlist").fetchall() == [
            (identifier,)
        ]
        assert connection.execute("PRAGMA table_info(billing_events)").fetchall()
        assert connection.execute("PRAGMA table_info(billing_subscriptions)").fetchall()
        assert connection.execute("SELECT count(*) FROM billing_events").fetchone() == (
            0,
        )
    downgraded = migrate(path, "downgrade", "20261030_0004")
    assert downgraded.returncode == 0, downgraded.stderr
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT id FROM watchlist").fetchall() == [
            (identifier,)
        ]
        assert not connection.execute("PRAGMA table_info(billing_events)").fetchall()
        assert not connection.execute(
            "PRAGMA table_info(billing_subscriptions)"
        ).fetchall()


def test_naive_service_clock_never_records_financial_data(engine):
    with Session(engine) as session:
        with pytest.raises(ValueError, match="timezone"):
            service(session, NOW.replace(tzinfo=None)).process_event(paid())
    assert counts(engine) == (0, 0, 0)


def test_public_customer_models_cannot_supply_verified_event_json(engine):
    with Session(engine) as session:
        with pytest.raises(ValueError, match="trusted"):
            service(session).process_event(paid().model_dump())
    assert counts(engine) == (0, 0, 0)


@pytest.mark.parametrize(
    "scenario", ["future_gap", "after_cancel", "refund", "dispute", "unsupported"]
)
def test_quarantine_never_revokes_confirmed_paid_access_or_extends_its_end(
    engine, scenario
):
    process(engine)
    if scenario == "after_cancel":
        with Session(engine) as session:
            service(session).cancel(actor())
        rejected = paid(
            event_id="quarantine",
            paid_period_start=END,
            paid_period_end=datetime(2027, 1, 5, tzinfo=UTC),
        )
    elif scenario == "future_gap":
        rejected = paid(
            event_id="quarantine",
            paid_period_start=END + timedelta(days=1),
            paid_period_end=END + timedelta(days=31),
        )
    else:
        rejected = paid(event_id="quarantine", kind=scenario)
    assert process(engine, rejected).processing_status == "review_required"
    current = summary(engine)
    assert current.review_required and current.entitled
    assert (current.paid_period_start, current.paid_period_end) == (NOW, END)
    assert summary(engine, now=END - timedelta(microseconds=1)).entitled
    assert not summary(engine, now=END).entitled
    assert not summary(engine, now=END + timedelta(days=1)).entitled
    # Even a later otherwise-coherent paid event cannot invent a new grant while
    # review remains unresolved; existing confirmed access is a separate fact.
    next_payment = paid(
        event_id="while-review",
        paid_period_start=END,
        paid_period_end=datetime(2027, 1, 5, tzinfo=UTC),
    )
    assert process(engine, next_payment).processing_status == "review_required"
    assert summary(engine).paid_period_end == END
    assert summary(engine).entitled
