"""Provider-neutral monthly lifecycle, never a payment gateway or public paywall.

Only a separately reviewed adapter may invoke process_event with verified account
mapping/signatures. No price, grace period, invoice, VAT or refund policy is inferred.
Retained-until is visibility metadata, not authorization to purge financial records.
"""

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.exceptions import APIError, ResourceNotFoundError
from app.core.retention import RetentionPolicy
from app.models.audit import AuditEvent
from app.models.billing import BillingEventRecord, SubscriptionRecord
from app.repositories.audit import AuditRepository
from app.repositories.billing import BillingRepository
from app.schemas.billing import (
    BillingEventReceipt,
    BillingHistoryItem,
    BillingHistoryPage,
    BillingHistoryQuery,
    SubscriptionSummary,
    VerifiedBillingEvent,
)
from app.schemas.history import HistoryCursor
from app.security.identity import (
    SessionVerificationError,
    VerifiedSession,
    principal_key,
    validate_customer_session,
)
from app.services.history_mutations import AuditPolicy


class BillingPolicy(RetentionPolicy):
    """Purpose-specific reviewed policy; no implicit retention duration."""


def _utc(value: datetime) -> datetime:
    # SQLite stores naive UTC; service/event clocks must instead be explicitly aware.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _fingerprint(event: VerifiedBillingEvent) -> str:
    body = json.dumps(
        event.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _known_unique_race(error: IntegrityError) -> bool:
    constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
    if constraint in {"uq_billing_owner", "uq_billing_provider_event"}:
        return True
    # SQLite supplies columns rather than named constraints. Never expose this text.
    message = str(error.orig)
    return any(
        value in message
        for value in (
            "UNIQUE constraint failed: billing_subscriptions.owner_key",
            "UNIQUE constraint failed: billing_events.provider, "
            "billing_events.provider_event_id",
        )
    )


class BillingService:
    """Writes own a fresh transaction; callers must not nest an active session."""

    def __init__(
        self,
        session: Session,
        *,
        policy: BillingPolicy | None = None,
        audit_policy: AuditPolicy | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._session = session
        self._policy = (
            BillingPolicy.model_validate(policy.model_dump(warnings="error"))
            if policy is not None
            else None
        )
        self._audit_policy = (
            AuditPolicy.model_validate(audit_policy.model_dump(warnings="error"))
            if audit_policy is not None
            else None
        )
        self._clock = clock
        self._repository = BillingRepository(session)
        self._audit = AuditRepository(session)

    def _now(self) -> datetime:
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Billing clock must be timezone aware")
        return now.astimezone(UTC)

    def _policy_required(self, *, writing: bool = False) -> None:
        if self._policy is None or (writing and self._audit_policy is None):
            raise APIError(503, "billing_unavailable", "Billing is unavailable")

    def _access(self, identity: VerifiedSession) -> tuple[str, datetime]:
        self._policy_required()
        now = self._now()
        try:
            actor = validate_customer_session(identity, now)
        except SessionVerificationError as error:
            raise APIError(401, "authentication_required", "Access denied") from error
        return principal_key(actor), now

    @staticmethod
    def _summary(
        record: SubscriptionRecord | None, now: datetime
    ) -> SubscriptionSummary:
        if record is None or _utc(record.retained_until) <= now:
            return SubscriptionSummary(
                state="none",
                entitled=False,
                paid_period_start=None,
                paid_period_end=None,
                cancel_at_period_end=False,
                renewal_consent=False,
                review_required=False,
            )
        start = _utc(record.paid_period_start) if record.paid_period_start else None
        end = _utc(record.paid_period_end) if record.paid_period_end else None
        state = "none"
        if record.review_required:
            state = "review_required"
        elif start is not None:
            state = "scheduled" if now < start else "active" if now < end else "expired"
        return SubscriptionSummary(
            state=state,
            # Quarantine is not permission to revoke an already confirmed paid
            # window. Refund/dispute outcomes require separately approved policy.
            entitled=bool(start is not None and start <= now < end),
            paid_period_start=start,
            paid_period_end=end,
            cancel_at_period_end=record.cancel_at_period_end,
            renewal_consent=record.renewal_consent,
            review_required=record.review_required,
        )

    def summary(self, identity: VerifiedSession) -> SubscriptionSummary:
        owner, _ = self._access(identity)
        record = self._repository.subscription(owner)
        _, now = self._access(identity)
        return self._summary(record, now)

    def entitled(self, identity: VerifiedSession) -> bool:
        return self.summary(identity).entitled

    def history(
        self, identity: VerifiedSession, query: BillingHistoryQuery
    ) -> BillingHistoryPage:
        owner, now = self._access(identity)
        if type(query.limit) is not int:
            raise ValueError("Billing page limit must be an integer")
        query = BillingHistoryQuery.model_validate(query.model_dump(warnings="error"))
        before = (
            (_utc(query.before_created_at), str(query.before_id))
            if query.before_created_at is not None
            else None
        )
        records = self._repository.history(owner, now, query.limit, before)
        _, now = self._access(identity)
        items = [
            BillingHistoryItem(
                id=UUID(row.id),
                kind=row.kind,
                amount_minor=(
                    str(row.amount_minor) if row.amount_minor is not None else None
                ),
                currency=row.currency,
                recorded_at=_utc(row.recorded_at),
                retained_until=_utc(row.retained_until),
                processing_status=row.processing_status,
            )
            for row in records
            if _utc(row.retained_until) > now
        ]
        return BillingHistoryPage(
            items=items,
            next_cursor=(
                HistoryCursor(created_at=items[-1].recorded_at, id=items[-1].id)
                if len(items) == query.limit
                else None
            ),
        )

    def _append_audit(self, owner: str, identifier: str, action: str) -> None:
        now = self._now()
        self._audit.append(
            AuditEvent(
                id=str(uuid4()),
                owner_key=owner,
                resource_id=identifier,
                action=action,
                occurred_at=now,
                expires_at=now
                + timedelta(seconds=self._audit_policy.retention_seconds),
                policy_reference=self._audit_policy.approval_reference,
            )
        )

    def cancel(self, identity: VerifiedSession) -> SubscriptionSummary:
        self._policy_required(writing=True)
        owner, _ = self._access(identity)
        try:
            with self._session.begin():
                record = self._repository.subscription(owner, lock=True)
                _, now = self._access(identity)
                if record is None or _utc(record.retained_until) <= now:
                    raise ResourceNotFoundError("Subscription")
                if not record.cancel_at_period_end:
                    record.cancel_at_period_end = True
                    record.renewal_consent = False
                    record.updated_at = now
                    self._append_audit(owner, record.id, "billing.cancelled")
                    self._access(identity)
                result = self._summary(record, now)
            return result
        except StaleDataError as error:
            raise APIError(
                409, "billing_retry_required", "Retry billing operation"
            ) from error

    def _new_subscription(self, owner: str, now: datetime) -> SubscriptionRecord:
        record = SubscriptionRecord(
            id=str(uuid4()),
            owner_key=owner,
            plan="monthly",
            paid_period_start=None,
            paid_period_end=None,
            cancel_at_period_end=False,
            renewal_consent=False,
            consent_reference=None,
            review_required=False,
            version=1,
            created_at=now,
            updated_at=now,
            retained_until=now + timedelta(seconds=self._policy.retention_seconds),
            policy_reference=self._policy.approval_reference,
        )
        self._repository.add(record)
        return record

    def _apply_paid(
        self,
        subscription: SubscriptionRecord,
        event: VerifiedBillingEvent,
        now: datetime,
    ) -> str | None:
        if subscription.review_required:
            return "review_pending"
        if event.occurred_at > now:
            return "future_event"
        start, end = event.paid_period_start, event.paid_period_end
        previous_end = (
            _utc(subscription.paid_period_end) if subscription.paid_period_end else None
        )
        if previous_end is None:
            subscription.paid_period_start = start
            subscription.renewal_consent = event.renewal_consent
            subscription.consent_reference = event.consent_reference
        else:
            if subscription.cancel_at_period_end:
                return "cancelled_renewal_requires_review"
            if not subscription.renewal_consent:
                return "renewal_consent_required"
            if start < previous_end:
                return "overlapping_paid_period"
            if start > previous_end:
                if now < previous_end:
                    return "disjoint_future_period"
                subscription.paid_period_start = start
        subscription.paid_period_end = end
        subscription.updated_at = now
        retained_until = end + timedelta(seconds=self._policy.retention_seconds)
        if retained_until > _utc(subscription.retained_until):
            subscription.retained_until = retained_until
            subscription.policy_reference = self._policy.approval_reference
        return None

    @staticmethod
    def _receipt(row: BillingEventRecord, *, duplicate: bool) -> BillingEventReceipt:
        return BillingEventReceipt(
            id=UUID(row.id),
            processing_status=row.processing_status,
            duplicate=duplicate,
        )

    def process_event(self, event: VerifiedBillingEvent) -> BillingEventReceipt:
        self._policy_required(writing=True)
        if not isinstance(event, VerifiedBillingEvent):
            raise ValueError("A trusted verified billing event is required")
        event = VerifiedBillingEvent.model_validate(event.model_dump(warnings="error"))
        fingerprint = _fingerprint(event)
        now = self._now()
        try:
            with self._session.begin():
                row = self._repository.event(event.provider, event.event_id)
                if row is not None:
                    if row.fingerprint == fingerprint:
                        return self._receipt(row, duplicate=True)
                    if row.review_reason != "event_fingerprint_conflict":
                        row.processing_status = "review_required"
                        row.review_reason = "event_fingerprint_conflict"
                        subscription = self._repository.subscription(
                            row.owner_key, lock=True
                        )
                        if subscription is not None:
                            subscription.review_required = True
                            subscription.updated_at = now
                        self._append_audit(
                            row.owner_key, row.id, "billing.event_conflict"
                        )
                    return self._receipt(row, duplicate=False)
                row = BillingEventRecord(
                    id=str(uuid4()),
                    owner_key=event.owner_key,
                    provider=event.provider,
                    provider_event_id=event.event_id,
                    fingerprint=fingerprint,
                    kind=event.kind,
                    occurred_at=event.occurred_at,
                    recorded_at=now,
                    retained_until=max(now, event.paid_period_end or now)
                    + timedelta(seconds=self._policy.retention_seconds),
                    policy_reference=self._policy.approval_reference,
                    amount_minor=event.amount_minor,
                    currency=event.currency,
                    paid_period_start=event.paid_period_start,
                    paid_period_end=event.paid_period_end,
                    processing_status="applied",
                    review_reason=None,
                )
                # First flush starts an actual transaction before any subsequent
                # writes. No legacy SQLite SAVEPOINT-only early commit hazard.
                self._repository.add(row)
                subscription = self._repository.subscription(event.owner_key, lock=True)
                reason = None
                if event.occurred_at > now:
                    reason = "future_event"
                elif event.kind == "paid":
                    if subscription is None:
                        subscription = self._new_subscription(event.owner_key, now)
                    reason = self._apply_paid(subscription, event, now)
                elif event.kind != "payment_failed":
                    reason = "unsupported_event_requires_review"
                if reason is not None:
                    row.processing_status = "review_required"
                    row.review_reason = reason
                    if subscription is None:
                        subscription = self._new_subscription(event.owner_key, now)
                    subscription.review_required = True
                    subscription.updated_at = now
                self._append_audit(event.owner_key, row.id, "billing.event_recorded")
                receipt = self._receipt(row, duplicate=False)
            return receipt
        except StaleDataError as error:
            raise APIError(
                409, "billing_retry_required", "Retry billing operation"
            ) from error
        except IntegrityError as error:
            if _known_unique_race(error):
                raise APIError(
                    409, "billing_retry_required", "Retry billing operation"
                ) from error
            raise
