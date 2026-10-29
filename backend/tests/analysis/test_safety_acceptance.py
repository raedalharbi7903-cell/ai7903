from math import nan

import pytest

from app.analysis.context import AnalysisContext
from app.analysis.engines import BaseEngine, RiskEngine, default_engines
from app.analysis.models import (
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    MarketData,
    ValidationStatus,
)
from app.analysis.service import AnalysisService
from tests.analysis.test_decision_states import complete_input
from tests.analysis.test_pipeline import fixture_input


def risk_context(decision, stop, target=None, atr=None) -> AnalysisContext:
    source = fixture_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    context.state["decision"] = decision
    context.add_output(
        EngineOutput(
            engine_name="market_structure",
            status=EngineLifecycleStatus.COMPLETED,
            data={"invalidation": stop},
        )
    )
    if target is not None:
        context.add_output(
            EngineOutput(
                engine_name="support_resistance",
                status=EngineLifecycleStatus.COMPLETED,
                data={"resistance": target, "support": target},
            )
        )
    if atr is not None:
        context.add_output(
            EngineOutput(
                engine_name="volatility",
                status=EngineLifecycleStatus.COMPLETED,
                data={"atr": atr},
            )
        )
    return context


@pytest.mark.parametrize(
    ("decision", "stop", "target"),
    [
        (DecisionState.BUY, 10, 13),
        (DecisionState.SELL, 16, 15),
        (DecisionState.BUY, 10, 14),
        (DecisionState.SELL, 16, 14),
        (DecisionState.BUY, None, 20),
        (DecisionState.BUY, 14, 20),
        (DecisionState.SELL, 14, 10),
        (DecisionState.BUY, nan, 20),
        (DecisionState.BUY, 10, nan),
        (DecisionState.BUY, 10, 0),
        (DecisionState.SELL, 30, None),
    ],
)
def test_unsafe_geometry_is_rejected(decision, stop, target) -> None:
    result = RiskEngine().analyze(risk_context(decision, stop, target))
    assert result.status != EngineLifecycleStatus.COMPLETED
    assert "target" not in result.data


@pytest.mark.parametrize(
    ("decision", "stop", "target"),
    [(DecisionState.BUY, 10, 15), (DecisionState.SELL, 18, 13)],
)
def test_poor_structural_reward_is_not_replaced_with_optimistic_projection(
    decision, stop, target
) -> None:
    result = RiskEngine().analyze(risk_context(decision, stop, target))
    assert result.status == EngineLifecycleStatus.FAILED
    assert result.data["risk_reward"] == 0.25


def test_missing_target_is_explicit_projection_not_observed_level() -> None:
    result = RiskEngine().analyze(risk_context(DecisionState.BUY, 10))
    assert result.data["target_source"] == "projection"
    assert result.data["target"] == 22
    assert result.data["risk_quality"] == "structural_without_volatility"
    assert result.data["liquidity_context"] == "unavailable"


@pytest.mark.parametrize(("stop", "reason"), [(13.5, "tight"), (1, "wide")])
def test_stop_volatility_limits(stop, reason) -> None:
    result = RiskEngine().analyze(risk_context(DecisionState.BUY, stop, atr=2))
    assert result.status == EngineLifecycleStatus.FAILED
    assert reason in result.warnings[0]


@pytest.mark.parametrize("minimum", [0, -1, nan, float("inf")])
def test_invalid_rr_policy_rejected(minimum) -> None:
    context = risk_context(DecisionState.BUY, 10)
    context.analysis_input.metadata["minimum_risk_reward"] = minimum
    assert RiskEngine().analyze(context).status == EngineLifecycleStatus.FAILED


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("close", 0),
        ("high", nan),
        ("low", -1),
        ("volume", -1),
        ("open", float("inf")),
    ],
)
def test_invalid_data_cannot_reach_actionable_decision(field, value) -> None:
    source = complete_input()
    source.data["candles"][-1][field] = value
    result = AnalysisService().analyze(source)
    assert result.decision == DecisionState.INSUFFICIENT_DATA
    assert result.validation == ValidationStatus.FAIL
    assert all(not o.evidence for o in result.outputs)


def test_non_independent_family_conflict_blocks_actionable_decision() -> None:
    class ContradictoryMomentum(BaseEngine):
        name, family = "contradictory_momentum", "momentum"

        def analyze(self, context):
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.COMPLETED,
                evidence=[
                    self.finding(context, "opposing same-family finding", "bearish")
                ],
            )

    engines = list(default_engines())
    index = next(i for i, e in enumerate(engines) if e.name == "evidence")
    engines.insert(index, ContradictoryMomentum())
    result = AnalysisService(engines=tuple(engines)).analyze(complete_input())
    outputs = {o.engine_name: o for o in result.outputs}
    assert outputs["contradictory_momentum"].evidence[0].independent is False
    assert outputs["confluence"].data["conflicted_families"] == ["momentum"]
    assert result.decision == DecisionState.NO_TRADE


def test_explanation_uses_final_safety_decision() -> None:
    source = fixture_input()
    source.metadata["timeframes"] = {
        name: source.data for name in ("htf", "itf", "ltf")
    }
    result = AnalysisService().analyze(source)
    explanation = next(o for o in result.outputs if o.engine_name == "explainability")
    assert result.decision == DecisionState.NO_TRADE
    assert explanation.data["summary"] == "Decision: no_trade"


def test_invalid_engine_configuration_fails_closed_through_service() -> None:
    source = complete_input()
    source.metadata["engine_configuration"] = {
        "momentum_divergence": {"left_window": 0}
    }
    result = AnalysisService().analyze(source)
    assert result.decision == DecisionState.NO_TRADE
    assert result.validation == ValidationStatus.FAIL
