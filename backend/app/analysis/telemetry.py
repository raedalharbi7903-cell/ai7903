"""Low-overhead, in-process observability hooks for the future Command Center."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AnalysisTelemetry:
    request_id: str
    status: str
    duration_ms: float
    provider: str | None
    data_quality: str | None
    freshness: str | None
    mtf_state: str | None
    evidence_families: int
    decision: str
    validation: str
    confidence: str | None
    risk_reason: str | None
    candle_count: int
    timeframe_analysis_count: int
    benchmark_observation_count: int
    engine_duration_ms: dict[str, float]
    analysis_version: str = "analysis-pipeline-v1"


@dataclass(frozen=True)
class BacktestTelemetry:
    event: str
    backtest_id: str
    duration_ms: float
    historical_analysis_count: int
    validated_decision_count: int
    rejected_decision_count: int
    executed_trade_count: int
    parameter_version: str
    strategy_version: str
    analysis_version: str
    data_source: str
    error_category: str | None = None


class TelemetrySink(Protocol):
    def record_analysis(self, event: AnalysisTelemetry) -> None: ...

    def record_backtest(self, event: BacktestTelemetry) -> None: ...


class NullTelemetrySink:
    def record_analysis(self, event: AnalysisTelemetry) -> None:
        return None

    def record_backtest(self, event: BacktestTelemetry) -> None:
        return None


class InMemoryTelemetrySink:
    """Test and local-development sink; callers own retention policy."""

    def __init__(self) -> None:
        self.events: list[AnalysisTelemetry] = []
        self.backtest_events: list[BacktestTelemetry] = []

    def record_analysis(self, event: AnalysisTelemetry) -> None:
        self.events.append(event)

    def record_backtest(self, event: BacktestTelemetry) -> None:
        self.backtest_events.append(event)
