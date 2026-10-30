from time import perf_counter
from uuid import uuid4

from app.analysis.context import AnalysisContext
from app.analysis.contracts import AnalysisEngine
from app.analysis.engines import default_engines
from app.analysis.grounded_ai import GroundedExplanationService
from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.pipeline import AnalysisPipeline
from app.analysis.telemetry import AnalysisTelemetry, NullTelemetrySink, TelemetrySink


class AnalysisService:
    def __init__(
        self,
        telemetry: TelemetrySink | None = None,
        engines: tuple[AnalysisEngine, ...] | None = None,
        *,
        explanation: GroundedExplanationService | None = None,
    ) -> None:
        self._telemetry = telemetry or NullTelemetrySink()
        self._engines = engines
        self._explanation = explanation

    def analyze(self, analysis_input: AnalysisInput) -> AnalysisResult:
        request_id = str(analysis_input.metadata.get("request_id", uuid4()))
        # Engines share this request-owned snapshot, never caller-owned objects.
        # This also prevents in-place frame normalization from changing replay data.
        context = AnalysisContext(analysis_input.model_copy(deep=True))
        started = perf_counter()
        result = AnalysisPipeline(
            self._engines or default_engines(explanation=self._explanation)
        ).run(context)
        confidence = context.output("confidence")
        risk = context.output("risk")
        try:
            self._telemetry.record_analysis(
                AnalysisTelemetry(
                    request_id=request_id,
                    status=result.status,
                    duration_ms=round((perf_counter() - started) * 1000, 3),
                    provider=(
                        context.market_data.provider if context.market_data else None
                    ),
                    data_quality=(
                        str(context.market_data.quality_status)
                        if context.market_data
                        else None
                    ),
                    freshness=(
                        str(context.market_data.freshness_status)
                        if context.market_data
                        else None
                    ),
                    mtf_state=context.state.get("mtf_alignment"),
                    evidence_families=len(
                        {item.family for item in context.evidence if item.independent}
                    ),
                    decision=result.decision,
                    validation=result.validation,
                    confidence=(
                        str(confidence.data.get("confidence")) if confidence else None
                    ),
                    risk_reason=(
                        "; ".join(risk.warnings) if risk and risk.warnings else None
                    ),
                    candle_count=(
                        len(context.market_data.candles) if context.market_data else 0
                    ),
                    timeframe_analysis_count=len(
                        context.analysis_input.metadata.get("timeframes", {})
                    ),
                    benchmark_observation_count=len(
                        context.analysis_input.metadata.get("benchmark_candles", [])
                    ),
                    engine_duration_ms=context.state.get("engine_duration_ms", {}),
                )
            )
        except Exception:
            # Telemetry is intentionally isolated from analysis correctness.
            pass
        return result
