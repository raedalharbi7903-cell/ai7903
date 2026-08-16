from app.analysis.context import AnalysisContext
from app.analysis.contracts import AnalysisEngine
from app.analysis.models import (
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
            context.add_output(engine.execute(context))
        validation = context.state.get("validation")
        if validation is None:
            return AnalysisResult(
                status=EngineLifecycleStatus.COMPLETED,
                outputs=context.outputs,
            )
        return AnalysisResult(
            status=(
                EngineLifecycleStatus.COMPLETED
                if validation == ValidationStatus.PASS
                else EngineLifecycleStatus.DEGRADED
            ),
            outputs=context.outputs,
            decision=context.state.get("decision", DecisionState.INSUFFICIENT_DATA),
            validation=validation,
        )
