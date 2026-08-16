from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class EngineLifecycleStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEGRADED = "degraded"


class ValidationStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    DEGRADED = "degraded"


class DecisionState(StrEnum):
    BUY = "buy"
    SELL = "sell"
    NO_TRADE = "no_trade"
    INSUFFICIENT_DATA = "insufficient_data"
    WAIT = "wait"


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class MarketData(BaseModel):
    instrument: str
    market: str
    timeframe: str
    provider: str
    exchange: str | None = None
    asset_type: str | None = None
    source_timestamp: datetime
    candles: list[Candle]
    fixture: bool = False
    quality_status: ValidationStatus = ValidationStatus.PASS

    @model_validator(mode="after")
    def has_candles(self) -> "MarketData":
        if not self.candles:
            raise ValueError("Market data must contain at least one candle")
        return self


class AnalysisInput(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    evidence_id: str
    source_engine: str
    family: str
    instrument: str
    market: str
    timeframe: str
    timestamp: datetime
    finding: str
    bias: str | None = None
    provenance: dict[str, str] = Field(default_factory=dict)
    independent: bool = True
    conflicts: list[str] = Field(default_factory=list)


class EngineOutput(BaseModel):
    engine_name: str
    status: EngineLifecycleStatus
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    status: EngineLifecycleStatus
    outputs: list[EngineOutput] = Field(default_factory=list)
    decision: DecisionState = DecisionState.INSUFFICIENT_DATA
    validation: ValidationStatus = ValidationStatus.FAIL
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
