"""Protected history reads. No public save, deletion or identity creation here."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.api.v1.analysis import prepare_analysis_input
from app.config.settings import Settings, get_settings
from app.core.exceptions import ResourceNotFoundError
from app.dependencies.history import (
    CustomerIdentity,
    get_history_mutations,
    get_history_service,
    private_history_response,
)
from app.schemas.analysis import AnalysisRequest
from app.schemas.history import HistoryEntry, HistoryPage, HistoryQuery
from app.services.analysis_history import AnalysisHistoryService
from app.services.history_mutations import HistoryMutationService

router = APIRouter(
    prefix="/history",
    tags=["history"],
    dependencies=[Depends(private_history_response)],
)
HistoryService = Annotated[AnalysisHistoryService, Depends(get_history_service)]
HistoryWriter = Annotated[HistoryMutationService, Depends(get_history_mutations)]


@router.get(
    "",
    response_model=HistoryPage,
    summary="List the current customer's saved analysis headers",
    description=(
        "Private metadata only. Verified identity and history policy required. "
        "A full-page cursor may lead to an empty page."
    ),
    responses={
        401: {"description": "Authentication required"},
        503: {"description": "History is not enabled"},
    },
)
def list_history(
    service: HistoryService,
    identity: CustomerIdentity,
    query: Annotated[HistoryQuery, Query()],
) -> HistoryPage:
    before = (
        (query.before_created_at, query.before_id)
        if query.before_created_at is not None and query.before_id is not None
        else None
    )
    return service.page(identity, limit=query.limit, before=before)


@router.get(
    "/{identifier}",
    response_model=HistoryEntry,
    summary="Read one unexpired analysis owned by the current customer",
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Record unavailable"},
        503: {"description": "History is not enabled"},
    },
)
def get_history(
    identifier: UUID,
    service: HistoryService,
    identity: CustomerIdentity,
) -> HistoryEntry:
    entry = service.get(identity, identifier)
    if entry is None:
        raise ResourceNotFoundError("Analysis history")
    return entry


@router.post(
    "",
    response_model=HistoryEntry,
    status_code=201,
    summary="Explicitly analyze and save an approved fixture with atomic audit",
    description=(
        "Trusted identity, enabled policies and exact Origin required. "
        "Development/testing fixture only; no client analysis results accepted."
    ),
)
def create_history(
    request: AnalysisRequest,
    writer: HistoryWriter,
    identity: CustomerIdentity,
    settings: Annotated[Settings, Depends(get_settings)],
) -> HistoryEntry:
    return writer.create(identity, prepare_analysis_input(request, settings))


@router.delete(
    "/{identifier}",
    status_code=204,
    response_class=Response,
    summary="Delete only an owned saved analysis with atomic audit",
)
def delete_history(
    identifier: UUID,
    writer: HistoryWriter,
    identity: CustomerIdentity,
) -> None:
    writer.delete(identity, identifier)
