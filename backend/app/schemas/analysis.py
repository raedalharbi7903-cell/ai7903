"""Explicit development-fixture request boundary; no implicit provider acquisition."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.analysis.advanced import (
    DivergenceConfig,
    StructureConfig,
    SweepConfig,
    VolumeConfig,
)
from app.analysis.freshness import TIMEFRAME_SECONDS
from app.analysis.models import Candle, MarketData, ValidationStatus
from app.analysis.providers import validate_market_data

CONFIGURATIONS = {
    "momentum_divergence": DivergenceConfig,
    "market_transition": StructureConfig,
    "liquidity_sweep": SweepConfig,
    "volume_anomaly": VolumeConfig,
}


def validate_fixture(data: MarketData) -> MarketData:
    if not data.fixture:
        raise ValueError("Only explicitly labeled fixture data is accepted")
    if data.market not in {"crypto", "fixture"} or data.asset_type not in {
        None,
        "crypto",
        "spot",
    }:
        raise ValueError("Only cryptocurrency spot fixture analysis is supported")
    if not data.provider.strip() or data.source_timestamp.tzinfo is None:
        raise ValueError("Provider and timezone-aware source timestamp are required")
    if len(data.candles) > 5000:
        raise ValueError("A fixture may contain at most 5000 candles")
    if validate_market_data(data) != ValidationStatus.PASS:
        raise ValueError("Fixture contains invalid candle data")
    return data


class AnalysisMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timeframes: dict[Literal["htf", "itf", "ltf"], MarketData] = Field(
        default_factory=dict
    )
    decision_timestamp: datetime | None = None
    benchmark_candles: list[Candle] = Field(default_factory=list, max_length=5000)
    engine_configuration: dict[str, dict[str, Any]] = Field(default_factory=dict)
    minimum_risk_reward: float = Field(default=1.0, ge=1, allow_inf_nan=False)
    minimum_stop_atr_multiple: float = Field(default=0.5, ge=0.5, allow_inf_nan=False)
    maximum_stop_atr_multiple: float = Field(
        default=5.0, gt=0, le=5, allow_inf_nan=False
    )

    @field_validator("engine_configuration")
    @classmethod
    def configurations(
        cls, value: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        for name, configuration in value.items():
            factory = CONFIGURATIONS.get(name)
            if factory is None:
                raise ValueError("Unknown configurable engine")
            try:
                factory(**configuration)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid configuration for {name}") from error
        return value

    @field_validator("timeframes")
    @classmethod
    def fixtures(cls, value: dict[str, MarketData]) -> dict[str, MarketData]:
        for data in value.values():
            validate_fixture(data)
        return value

    @model_validator(mode="after")
    def policy(self) -> "AnalysisMetadata":
        if self.decision_timestamp and self.decision_timestamp.tzinfo is None:
            raise ValueError("Decision timestamp must include timezone")
        if self.maximum_stop_atr_multiple < self.minimum_stop_atr_multiple:
            raise ValueError("Stop policy bounds are inverted")
        return self


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pair: str = Field(min_length=3, max_length=32, pattern=r"^[A-Z0-9]+-[A-Z0-9]+$")
    timeframe: str
    request_id: str | None = Field(default=None, max_length=128)
    market_data: MarketData | None = None
    metadata: AnalysisMetadata = Field(default_factory=AnalysisMetadata)

    @field_validator("timeframe")
    @classmethod
    def supported_timeframe(cls, value: str) -> str:
        if value not in TIMEFRAME_SECONDS or value == "fixture":
            raise ValueError("Unsupported timeframe")
        return value

    @field_validator("market_data")
    @classmethod
    def fixture(cls, value: MarketData | None) -> MarketData | None:
        return validate_fixture(value) if value is not None else None

    @model_validator(mode="after")
    def provenance(self) -> "AnalysisRequest":
        if self.market_data is not None and (
            self.market_data.instrument != self.pair
            or self.market_data.timeframe != self.timeframe
        ):
            raise ValueError("Pair/timeframe must match fixture provenance")
        if any(
            frame.instrument != self.pair for frame in self.metadata.timeframes.values()
        ):
            raise ValueError("Timeframe instruments must match the primary pair")
        return self
