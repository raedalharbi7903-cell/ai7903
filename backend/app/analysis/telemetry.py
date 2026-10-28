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
    analysis_version: str = "analysis-pipeline-v1"


class TelemetrySink(Protocol):
    def record_analysis(self, event: AnalysisTelemetry) -> None: ...


class NullTelemetrySink:
    def record_analysis(self, event: AnalysisTelemetry) -> None:
        return None


class InMemoryTelemetrySink:
    """Test and local-development sink; callers own retention policy."""

    def __init__(self) -> None:
        self.events: list[AnalysisTelemetry] = []

    def record_analysis(self, event: AnalysisTelemetry) -> None:
        self.events.append(event)
