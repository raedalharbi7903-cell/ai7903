from math import isfinite
from time import perf_counter

import structlog

from app.analysis.context import AnalysisContext
from app.analysis.contracts import AnalysisEngine
from app.analysis.models import (
    AdvancedFinding,
    AnalysisResult,
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    ValidationStatus,
)


class AnalysisPipeline:
    def __init__(self, engines: tuple[AnalysisEngine, ...]) -> None:
        self._engines = engines

    def run(self, context: AnalysisContext) -> AnalysisResult:
        for engine in self._engines:
            started = perf_counter()
            try:
                output = engine.execute(context)
                _validate_finite_output(output.model_dump())
            except Exception as error:
                structlog.get_logger(__name__).error(
                    "analysis_engine_failed",
                    engine=engine.name,
                    error_category=type(error).__name__,
                )
                output = EngineOutput(
                    engine_name=engine.name,
                    status=EngineLifecycleStatus.FAILED,
                    warnings=["engine execution failed"],
                )
            context.add_output(output)
            context.state.setdefault("engine_duration_ms", {})[engine.name] = round(
                (perf_counter() - started) * 1000, 3
            )
        # Final reconciliation also covers failures after the validation engine.
        # A late failure must not leave a stale actionable decision/explanation.
        if any(o.status == EngineLifecycleStatus.FAILED for o in context.outputs):
            context.state["validation"] = ValidationStatus.FAIL
            context.state["decision"] = (
                DecisionState.NO_TRADE
                if context.market_data
                else DecisionState.INSUFFICIENT_DATA
            )
            validation_output = context.output("validation")
            if validation_output is not None:
                validation_output.data["validation"] = ValidationStatus.FAIL
                reasons = validation_output.data.setdefault("reasons", [])
                if "required engine failed" not in reasons:
                    reasons.append("required engine failed")
            explanation = context.output("explainability")
            if explanation is not None:
                explanation.data["summary"] = f"Decision: {context.state['decision']}"
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


def _validate_finite_output(value: object) -> None:
    """Do not publish nonfinite measurements as nulls or invalid JSON."""
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Engine produced a nonfinite measurement")
    if isinstance(value, dict):
        for item in value.values():
            _validate_finite_output(item)
    elif isinstance(value, list | tuple):
        for item in value:
            _validate_finite_output(item)


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
