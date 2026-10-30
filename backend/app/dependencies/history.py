"""Private read dependencies; auth and release gates run before opening a DB."""

from typing import Annotated

from fastapi import Depends, Response

from app.config.settings import Settings, get_settings
from app.core.exceptions import APIError
from app.dependencies.factories import DatabaseSession
from app.repositories.analysis_history import AnalysisHistoryRepository
from app.security.dependencies import require_customer_session
from app.security.identity import VerifiedSession
from app.services.analysis_history import AnalysisHistoryService, HistoryPolicy

CustomerIdentity = Annotated[VerifiedSession, Depends(require_customer_session)]


def private_history_response(response: Response) -> None:
    response.headers["Cache-Control"] = "private, no-store"


def require_history_policy(
    _identity: CustomerIdentity,
    settings: Annotated[Settings, Depends(get_settings)],
) -> HistoryPolicy:
    if (
        not settings.history_enabled
        or settings.history_retention_seconds is None
        or settings.history_policy_reference is None
    ):
        raise APIError(503, "history_unavailable", "Analysis history is unavailable")
    return HistoryPolicy(
        retention_seconds=settings.history_retention_seconds,
        approval_reference=settings.history_policy_reference,
    )


def get_history_service(
    policy: Annotated[HistoryPolicy, Depends(require_history_policy)],
    session: DatabaseSession,
) -> AnalysisHistoryService:
    return AnalysisHistoryService(AnalysisHistoryRepository(session), policy=policy)
