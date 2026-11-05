"""Billing authorization/provider gates precede body verification and DB access."""

from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_core import PydanticSerializationError
from starlette.requests import ClientDisconnect

from app.config.settings import Settings, get_settings
from app.core.exceptions import APIError
from app.dependencies.factories import DatabaseSession
from app.dependencies.history import CustomerIdentity
from app.schemas.billing import VerifiedBillingEvent
from app.security.origin import require_exact_origin
from app.security.payment_events import (
    BillingEventVerificationError,
    BillingEventVerifier,
    UnconfiguredBillingEventVerifier,
)
from app.services.billing import BillingPolicy, BillingService
from app.services.history_mutations import AuditPolicy

MAX_BILLING_EVENT_BYTES = 64 * 1024


class CancellationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


def get_billing_event_verifier() -> BillingEventVerifier:
    return UnconfiguredBillingEventVerifier()


def configured_policy(settings: Settings) -> BillingPolicy:
    if (
        not settings.billing_enabled
        or settings.billing_retention_seconds is None
        or settings.billing_policy_reference is None
    ):
        raise APIError(503, "billing_unavailable", "Billing is unavailable")
    return BillingPolicy(
        retention_seconds=settings.billing_retention_seconds,
        approval_reference=settings.billing_policy_reference,
    )


def configured_audit(settings: Settings) -> AuditPolicy:
    if (
        settings.billing_audit_retention_seconds is None
        or settings.billing_audit_policy_reference is None
    ):
        raise APIError(
            503, "billing_mutation_unavailable", "Billing writing unavailable"
        )
    return AuditPolicy(
        retention_seconds=settings.billing_audit_retention_seconds,
        approval_reference=settings.billing_audit_policy_reference,
    )


def require_customer_billing_policy(
    _identity: CustomerIdentity,
    settings: Annotated[Settings, Depends(get_settings)],
) -> BillingPolicy:
    return configured_policy(settings)


async def require_cancellation_policies(
    policy: Annotated[BillingPolicy, Depends(require_customer_billing_policy)],
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> tuple[BillingPolicy, AuditPolicy]:
    audit = configured_audit(settings)
    if settings.billing_allowed_origin is None:
        raise APIError(
            503, "billing_mutation_unavailable", "Billing writing unavailable"
        )
    require_exact_origin(
        request, settings.billing_allowed_origin, "billing_origin_rejected"
    )
    payload = await bounded_billing_body(request)
    try:
        CancellationRequest.model_validate_json(payload)
    except ValidationError as error:
        raise APIError(422, "validation_error", "Request validation failed") from error
    return policy, audit


async def require_verified_billing_event(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    verifier: Annotated[BillingEventVerifier, Depends(get_billing_event_verifier)],
) -> VerifiedBillingEvent:
    configured_policy(settings)
    configured_audit(settings)
    if (
        settings.billing_provider_id is None
        or settings.billing_provider_approval_reference is None
        or isinstance(verifier, UnconfiguredBillingEventVerifier)
    ):
        raise APIError(
            503, "billing_provider_unavailable", "Billing provider unavailable"
        )
    try:
        matches_provider = verifier.provider_id == settings.billing_provider_id
    except Exception as error:
        raise APIError(
            503, "billing_provider_unavailable", "Billing provider unavailable"
        ) from error
    if not matches_provider:
        raise APIError(
            503, "billing_provider_unavailable", "Billing provider unavailable"
        )
    body = await bounded_billing_body(request)
    try:
        event = await verifier.verify(body, request.headers)
    except BillingEventVerificationError as error:
        raise APIError(
            401, "billing_event_authentication_required", "Access denied"
        ) from error
    except Exception as error:
        raise APIError(
            503,
            "billing_event_verification_unavailable",
            "Event verification unavailable",
        ) from error
    try:
        if not isinstance(event, VerifiedBillingEvent):
            raise ValueError("Untrusted event result")
        event = VerifiedBillingEvent.model_validate(event.model_dump(warnings="error"))
        if event.provider != settings.billing_provider_id:
            raise ValueError("Untrusted event provider")
    except (ValidationError, PydanticSerializationError, ValueError) as error:
        raise APIError(
            401, "billing_event_authentication_required", "Access denied"
        ) from error
    return event


async def bounded_billing_body(request: Request) -> bytes:
    """Cap raw billing input before parsing; declared lengths are not trusted."""
    lengths = request.headers.getlist("content-length")
    if lengths:
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            raise APIError(400, "billing_event_body_invalid", "Invalid event body")
        try:
            length = int(lengths[0])
        except ValueError as error:
            raise APIError(
                400, "billing_event_body_invalid", "Invalid event body"
            ) from error
        if length > MAX_BILLING_EVENT_BYTES:
            raise APIError(413, "billing_event_too_large", "Event body is too large")
    body = bytearray()
    try:
        async for chunk in request.stream():
            if len(chunk) > MAX_BILLING_EVENT_BYTES - len(body):
                raise APIError(
                    413, "billing_event_too_large", "Event body is too large"
                )
            body.extend(chunk)
    except ClientDisconnect as error:
        raise APIError(
            400, "billing_event_body_invalid", "Invalid event body"
        ) from error
    return bytes(body)


VerifiedEvent = Annotated[VerifiedBillingEvent, Depends(require_verified_billing_event)]


def get_billing_reader(
    policy: Annotated[BillingPolicy, Depends(require_customer_billing_policy)],
    session: DatabaseSession,
) -> BillingService:
    return BillingService(session, policy=policy)


def get_billing_cancellation(
    policies: Annotated[
        tuple[BillingPolicy, AuditPolicy], Depends(require_cancellation_policies)
    ],
    session: DatabaseSession,
) -> BillingService:
    policy, audit = policies
    return BillingService(session, policy=policy, audit_policy=audit)


def get_billing_event_processor(
    _event: VerifiedEvent,
    settings: Annotated[Settings, Depends(get_settings)],
    session: DatabaseSession,
) -> BillingService:
    return BillingService(
        session,
        policy=configured_policy(settings),
        audit_policy=configured_audit(settings),
    )
