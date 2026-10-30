"""Default-deny watchlist release/purpose/origin gates precede database opening."""

from typing import Annotated

from fastapi import Depends, Request

from app.config.settings import Settings, get_settings
from app.core.exceptions import APIError
from app.dependencies.factories import DatabaseSession
from app.dependencies.history import CustomerIdentity
from app.security.origin import require_exact_origin
from app.services.history_mutations import AuditPolicy
from app.services.watchlist import WatchlistPolicy, WatchlistService


def require_watchlist_policy(
    _identity: CustomerIdentity,
    settings: Annotated[Settings, Depends(get_settings)],
) -> WatchlistPolicy:
    if (
        not settings.watchlist_enabled
        or settings.watchlist_retention_seconds is None
        or settings.watchlist_policy_reference is None
    ):
        raise APIError(503, "watchlist_unavailable", "Watchlist is unavailable")
    return WatchlistPolicy(
        retention_seconds=settings.watchlist_retention_seconds,
        approval_reference=settings.watchlist_policy_reference,
    )


def require_watchlist_mutation(
    policy: Annotated[WatchlistPolicy, Depends(require_watchlist_policy)],
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> tuple[WatchlistPolicy, AuditPolicy]:
    if (
        settings.watchlist_allowed_origin is None
        or settings.watchlist_audit_retention_seconds is None
        or settings.watchlist_audit_policy_reference is None
    ):
        raise APIError(
            503, "watchlist_mutation_unavailable", "Watchlist writing unavailable"
        )
    require_exact_origin(
        request, settings.watchlist_allowed_origin, "watchlist_origin_rejected"
    )
    return policy, AuditPolicy(
        retention_seconds=settings.watchlist_audit_retention_seconds,
        approval_reference=settings.watchlist_audit_policy_reference,
    )


def get_watchlist(
    policy: Annotated[WatchlistPolicy, Depends(require_watchlist_policy)],
    session: DatabaseSession,
) -> WatchlistService:
    return WatchlistService(session, policy=policy)


def get_watchlist_writer(
    policies: Annotated[
        tuple[WatchlistPolicy, AuditPolicy], Depends(require_watchlist_mutation)
    ],
    session: DatabaseSession,
) -> WatchlistService:
    policy, audit = policies
    return WatchlistService(session, policy=policy, audit_policy=audit)
