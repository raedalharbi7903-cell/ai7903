"""Private billing views/cancellation and a separately authenticated event ingress."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies.billing import (
    CancellationRequest,
    VerifiedEvent,
    get_billing_cancellation,
    get_billing_event_processor,
    get_billing_reader,
)
from app.dependencies.history import CustomerIdentity, private_history_response
from app.schemas.billing import (
    BillingEventReceipt,
    BillingHistoryPage,
    BillingHistoryQuery,
    SubscriptionSummary,
)
from app.services.billing import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])
Reader = Annotated[BillingService, Depends(get_billing_reader)]
Cancellation = Annotated[BillingService, Depends(get_billing_cancellation)]
Processor = Annotated[BillingService, Depends(get_billing_event_processor)]
PRIVATE = [Depends(private_history_response)]


@router.get(
    "/subscription",
    response_model=SubscriptionSummary,
    dependencies=PRIVATE,
    summary="Read the trusted customer's recorded monthly entitlement",
)
def subscription(service: Reader, identity: CustomerIdentity) -> SubscriptionSummary:
    return service.summary(identity)


@router.get(
    "/history",
    response_model=BillingHistoryPage,
    dependencies=PRIVATE,
    summary="List the trusted customer's recorded billing events",
)
def billing_history(
    service: Reader,
    identity: CustomerIdentity,
    query: Annotated[BillingHistoryQuery, Query()],
) -> BillingHistoryPage:
    return service.history(identity, query)


@router.post(
    "/subscription/cancel",
    response_model=SubscriptionSummary,
    dependencies=PRIVATE,
    summary="Request recorded cancellation at the end of the paid period",
    description=(
        "Requires an empty JSON object, trusted identity, policies and Origin. "
        "This does not call a payment provider, initiate a refund or delete an account."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {"schema": CancellationRequest.model_json_schema()}
            },
        }
    },
)
def cancel_subscription(
    service: Cancellation,
    identity: CustomerIdentity,
) -> SubscriptionSummary:
    return service.cancel(identity)


@router.post(
    "/events",
    response_model=BillingEventReceipt,
    dependencies=PRIVATE,
    summary="Process an event only after trusted provider verification",
    description=(
        "Opaque body capped at 64 KiB; approved adapter must verify exact bytes "
        "and trusted account mapping. No adapter is configured by default. JSON fields "
        "or customer credentials never establish payment-event authenticity."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
        }
    },
)
def billing_event(event: VerifiedEvent, service: Processor) -> BillingEventReceipt:
    return service.process_event(event)
