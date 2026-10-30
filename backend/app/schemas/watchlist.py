"""Private spot watchlist metadata, never market prices or implicit analysis."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from app.analysis.freshness import TIMEFRAME_SECONDS
from app.schemas.history import HistoryCursor, HistoryQuery


class WatchlistInput(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    pair: str = Field(min_length=3, max_length=32, pattern=r"^[A-Z0-9]+-[A-Z0-9]+$")
    timeframe: str

    @field_validator("timeframe")
    @classmethod
    def supported_timeframe(cls, value: str) -> str:
        if value not in TIMEFRAME_SECONDS or value == "fixture":
            raise ValueError("Unsupported timeframe")
        return value


class WatchlistItem(WatchlistInput):
    # Database UUID/time values are converted explicitly for strict output.
    model_config = ConfigDict(frozen=True, extra="forbid")
    id: UUID
    created_at: AwareDatetime
    expires_at: AwareDatetime


class WatchlistQuery(HistoryQuery):
    """Same bounded paired keyset cursor contract, separate resource semantics."""


class WatchlistPage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    contract_version: Literal["1.0"] = "1.0"
    items: list[WatchlistItem]
    next_cursor: HistoryCursor | None = None
