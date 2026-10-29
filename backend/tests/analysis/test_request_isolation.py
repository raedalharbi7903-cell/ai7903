from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from app.analysis.context import AnalysisContext
from app.analysis.engines import BaseEngine, default_engines
from app.analysis.models import EngineLifecycleStatus, EngineOutput
from app.analysis.service import AnalysisService
from tests.analysis.test_decision_states import bearish_input, complete_input


def test_service_preserves_caller_owned_input_even_with_mutating_engine() -> None:
    class MutatingEngine(BaseEngine):
        name = "mutation-probe"

        def analyze(self, context: AnalysisContext) -> EngineOutput:
            context.analysis_input.metadata["nested"]["values"].append("changed")
            context.analysis_input.data["candles"][0]["close"] = -1
            return EngineOutput(
                engine_name=self.name, status=EngineLifecycleStatus.COMPLETED
            )

    source = complete_input()
    source.metadata["nested"] = {"values": ["original"]}
    before = deepcopy(source.model_dump())
    AnalysisService(engines=(*default_engines(), MutatingEngine())).analyze(source)
    assert source.model_dump() == before


def test_shared_service_keeps_parallel_requests_and_failures_isolated() -> None:
    service = AnalysisService()

    def run(index):
        source = bearish_input() if index % 2 else complete_input()
        symbol = f"FIXTURE{index}-USDT"
        source.data["instrument"] = symbol
        for frame in source.metadata["timeframes"].values():
            frame["instrument"] = symbol
        source.metadata["engine_configuration"] = {
            "momentum_divergence": {"left_window": 1 + index % 2}
        }
        if index % 5 == 0:
            source.metadata["freshness_policy"] = {"delayed_after_intervals": -1}
        before = deepcopy(source.model_dump())
        result = service.analyze(source)
        assert source.model_dump() == before
        assert len(result.outputs) == 28
        for output in result.outputs:
            assert all(item.instrument == symbol for item in output.evidence)
        if index % 5 == 0:
            assert result.validation.value == "fail"
            assert result.decision.value not in {"buy", "sell"}
        else:
            assert result.validation.value == "pass"
            assert result.decision.value == ("sell" if index % 2 else "buy")
        return result.decision

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(run, range(64)))
    assert len(results) == 64
