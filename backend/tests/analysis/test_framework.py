from app.analysis.context import AnalysisContext
from app.analysis.models import AnalysisInput, EngineLifecycleStatus, EngineOutput
from app.analysis.pipeline import AnalysisPipeline
from app.analysis.registry import EngineRegistry


class StubEngine:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def execute(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"previous_outputs": len(context.outputs)},
        )


def test_pipeline_runs_engines_in_sequence() -> None:
    pipeline = AnalysisPipeline((StubEngine("first"), StubEngine("second")))

    result = pipeline.run(AnalysisContext(analysis_input=AnalysisInput()))

    assert result.status is EngineLifecycleStatus.COMPLETED
    assert [output.engine_name for output in result.outputs] == ["first", "second"]
    assert result.outputs[1].data == {"previous_outputs": 1}


def test_registry_registers_and_discovers_engines() -> None:
    registry = EngineRegistry()
    engine = StubEngine("stub")

    registry.register(engine)

    assert registry.get("stub") is engine
    assert registry.all() == (engine,)
