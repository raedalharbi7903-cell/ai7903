"""Versioned private history read contract; list pages exclude full result blobs."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.analysis.models import AnalysisResult

MAX_HISTORY_PAGE_SIZE = 100
DEFAULT_HISTORY_PAGE_SIZE = 20


class HistoryHeader(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    id: UUID
    created_at: AwareDatetime
    expires_at: AwareDatetime


class HistoryEntry(HistoryHeader):
    result: AnalysisResult


class HistoryCursor(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    created_at: AwareDatetime
    id: UUID


class HistoryPage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    contract_version: Literal["1.0"] = "1.0"
    items: list[HistoryHeader]
    next_cursor: HistoryCursor | None = None


class HistoryQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(
        default=DEFAULT_HISTORY_PAGE_SIZE, ge=1, le=MAX_HISTORY_PAGE_SIZE
    )
    before_created_at: AwareDatetime | None = None
    before_id: UUID | None = None

    @model_validator(mode="after")
    def paired_cursor(self) -> "HistoryQuery":
        if (self.before_created_at is None) != (self.before_id is None):
            raise ValueError("Both history cursor fields must be supplied together")
        return self
