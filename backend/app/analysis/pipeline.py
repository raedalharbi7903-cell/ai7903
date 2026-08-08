from app.analysis.context import AnalysisContext
from app.analysis.contracts import AnalysisEngine
from app.analysis.models import AnalysisResult, EngineLifecycleStatus


class AnalysisPipeline:
    """Executes registered analysis engines sequentially."""

    def __init__(self, engines: tuple[AnalysisEngine, ...]) -> None:
        self._engines = engines

    def run(self, context: AnalysisContext) -> AnalysisResult:
        for engine in self._engines:
            context.add_output(engine.execute(context))
        return AnalysisResult(
            status=EngineLifecycleStatus.COMPLETED,
            outputs=context.outputs,
        )
