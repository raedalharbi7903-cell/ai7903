import pytest

from app.analysis.engines import BaseEngine, default_engines
from app.analysis.models import DecisionState, EngineLifecycleStatus, ValidationStatus
from app.analysis.service import AnalysisService
from app.analysis.telemetry import InMemoryTelemetrySink
from tests.analysis.test_decision_states import complete_input


@pytest.mark.parametrize("position", [1, 10, 24, 28])
def test_engine_exception_is_traceable_and_never_actionable(position) -> None:
    class BrokenEngine(BaseEngine):
        name = "broken_engine"

        def analyze(self, context):
            raise RuntimeError("secret-provider-token-and-internal-path")

    engines = list(default_engines())
    engines.insert(position, BrokenEngine())
    sink = InMemoryTelemetrySink()
    result = AnalysisService(sink, engines=tuple(engines)).analyze(complete_input())
    assert result.decision == DecisionState.NO_TRADE
    assert result.validation == ValidationStatus.FAIL
    assert len(result.outputs) == 29
    failed = next(o for o in result.outputs if o.engine_name == "broken_engine")
    assert failed.status == EngineLifecycleStatus.FAILED
    assert not failed.evidence
    assert "secret-provider-token" not in result.model_dump_json()
    explanation = next(o for o in result.outputs if o.engine_name == "explainability")
    assert explanation.data["summary"] == "Decision: no_trade"
    validation = next(o for o in result.outputs if o.engine_name == "validation")
    assert validation.data["validation"] == ValidationStatus.FAIL
    assert sink.events[-1].decision == DecisionState.NO_TRADE
