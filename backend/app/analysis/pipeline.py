from time import perf_counter

from app.analysis.context import AnalysisContext
from app.analysis.contracts import AnalysisEngine
from app.analysis.models import (
    AdvancedFinding,
    AnalysisResult,
    DecisionState,
    EngineLifecycleStatus,
    ValidationStatus,
)


class AnalysisPipeline:
    def __init__(self, engines: tuple[AnalysisEngine, ...]) -> None:
        self._engines = engines

    def run(self, context: AnalysisContext) -> AnalysisResult:
        for engine in self._engines:
            started = perf_counter()
            context.add_output(engine.execute(context))
            context.state.setdefault("engine_duration_ms", {})[engine.name] = round(
                (perf_counter() - started) * 1000, 3
            )
        validation = context.state.get("validation")
        if validation is None:
            return AnalysisResult(
                status=EngineLifecycleStatus.COMPLETED,
                outputs=context.outputs,
                advanced_findings=_advanced_findings(context),
            )
        return AnalysisResult(
            status=(
                EngineLifecycleStatus.COMPLETED
                if validation == ValidationStatus.PASS
                else EngineLifecycleStatus.DEGRADED
            ),
            outputs=context.outputs,
            decision=(
                DecisionState.INSUFFICIENT_DATA
                if context.market_data is None
                else (
                    context.state.get("decision", DecisionState.NO_TRADE)
                    if validation == ValidationStatus.PASS
                    else DecisionState.NO_TRADE
                )
            ),
            validation=validation,
            advanced_findings=_advanced_findings(context),
        )


def _advanced_findings(context: AnalysisContext) -> list[AdvancedFinding]:
    families = {
        "momentum_divergence": "momentum",
        "market_transition": "structure",
        "liquidity_sweep": "liquidity",
        "volume_anomaly": "volume",
        "candlestick": "candlestick",
    }
    findings: list[AdvancedFinding] = []
    for output in context.outputs:
        family = families.get(output.engine_name)
        if family is None:
            continue
        evidence = output.evidence[0] if output.evidence else None
        findings.append(
            AdvancedFinding(
                engine_id=output.engine_name,
                status=output.status,
                provenance=evidence.provenance if evidence else {},
                classification=output.data.get("classification"),
                direction=(evidence.bias if evidence else None),
                family=family,
                details=output.data,
                warnings=output.warnings,
            )
        )
    return findings
