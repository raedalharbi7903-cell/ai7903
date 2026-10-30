"""Private preferences only: no automatic scan, price retrieval or analysis."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.history import CustomerIdentity, private_history_response
from app.dependencies.watchlist import get_watchlist, get_watchlist_writer
from app.schemas.watchlist import (
    WatchlistInput,
    WatchlistItem,
    WatchlistPage,
    WatchlistQuery,
)
from app.services.watchlist import WatchlistService

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    dependencies=[Depends(private_history_response)],
)
Reader = Annotated[WatchlistService, Depends(get_watchlist)]
Writer = Annotated[WatchlistService, Depends(get_watchlist_writer)]


@router.get(
    "",
    response_model=WatchlistPage,
    summary="List owned unexpired watchlist preferences",
)
def list_watchlist(
    service: Reader,
    identity: CustomerIdentity,
    query: Annotated[WatchlistQuery, Query()],
) -> WatchlistPage:
    return service.page(identity, query)


@router.post(
    "",
    response_model=WatchlistItem,
    status_code=201,
    summary="Explicitly save a pair/timeframe preference",
    description=(
        "No provider availability is implied. New item returns 201; an active "
        "duplicate returns the unchanged existing item with 200 and no expiry renewal."
    ),
    responses={200: {"description": "Existing active owned preference"}},
)
def create_watchlist(
    payload: WatchlistInput,
    service: Writer,
    identity: CustomerIdentity,
    response: Response,
) -> WatchlistItem:
    item, created = service.create(identity, payload)
    if not created:
        response.status_code = 200
    return item


@router.delete("/{identifier}", status_code=204, response_class=Response)
def delete_watchlist(
    identifier: UUID,
    service: Writer,
    identity: CustomerIdentity,
) -> None:
    service.delete(identity, identifier)
