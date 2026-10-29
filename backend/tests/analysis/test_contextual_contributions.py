import pytest

from app.analysis.context import AnalysisContext
from app.analysis.deterministic import analyze
from app.analysis.engines import (
    ConfidenceEngine,
    ConfluenceEngine,
    DecisionEngine,
    LiquidityEngine,
    LiquiditySweepEngine,
    MarketContextEngine,
    OpportunityFilter,
    SupplyDemandEngine,
    SupportResistanceEngine,
)
from app.analysis.models import MarketData
from app.analysis.service import AnalysisService
from tests.analysis.test_advanced_behavior import candles
from tests.analysis.test_decision_states import bearish_input, complete_input

CONTEXTUAL = {"market_context", "support_resistance", "supply_demand", "liquidity"}


@pytest.mark.parametrize("factory", [complete_input, bearish_input])
def test_option_a_is_reached_through_actual_service(factory) -> None:
    result = AnalysisService().analyze(factory())
    selected = [o for o in result.outputs if o.engine_name in CONTEXTUAL]
    assert len(selected) == 4
    for output in selected:
        assert output.evidence
        assert all(item.bias is None for item in output.evidence)
        assert all(item.provenance["fixture"] == "True" for item in output.evidence)
    confluence = next(o for o in result.outputs if o.engine_name == "confluence")
    assert confluence.data["families"] == 5  # structure, trend, momentum, pattern, MTF
    confidence = next(o for o in result.outputs if o.engine_name == "confidence")
    assert confidence.data["independent_families"] == 5
    assert confidence.data["calibration"] == "uncalibrated"


def test_only_contextual_findings_cannot_create_confluence_or_actionable_decision() -> (
    None
):
    source = complete_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    for engine in (
        MarketContextEngine(),
        SupportResistanceEngine(),
        SupplyDemandEngine(),
        LiquidityEngine(),
        ConfluenceEngine(),
        OpportunityFilter(),
        DecisionEngine(),
        ConfidenceEngine(),
    ):
        context.add_output(engine.execute(context))
    assert context.output("confluence").data["families"] == 0
    assert context.output("confluence").data["aligned"] is False
    assert context.output("decision").data["decision"] == "no_trade"
    assert context.output("confidence").data["independent_families"] == 0
    assert context.output("confidence").data["confidence"] == "low"


@pytest.mark.parametrize("name", ["support_resistance", "supply_demand", "liquidity"])
def test_contextual_methods_keep_measurements_without_direction(name) -> None:
    state, direction, details = analyze(name, candles([10, 11, 12, 13, 14, 15]))
    assert state
    assert details
    assert direction is None


def test_sweep_keeps_its_own_confirmed_direction_without_a_basic_liquidity_vote() -> (
    None
):
    source = complete_input()
    data = MarketData.model_validate(source.data)
    data.candles = candles([10] * 7)
    data.candles[5].high = 12
    context = AnalysisContext(source, market_data=data)
    for engine in (LiquidityEngine(), LiquiditySweepEngine(), ConfluenceEngine()):
        context.add_output(engine.execute(context))
    assert context.output("liquidity").evidence[0].bias is None
    sweep = context.output("liquidity_sweep")
    assert sweep.data["classification"] == "confirmed_buy_side_sweep"
    assert sweep.evidence[0].bias == "bearish"
    assert sweep.evidence[0].family == "liquidity"
    assert sweep.evidence[0].independent is False  # existing family representative
    assert context.output("confluence").data["families"] == 1
    assert context.output("confluence").data["aligned"] is True


def test_contextual_observations_survive_api_serialization_without_votes() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    source = complete_input()
    source.data["instrument"] = "TEST-USDT"
    for frame in source.metadata["timeframes"].values():
        frame["instrument"] = "TEST-USDT"
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analysis",
            json={
                "pair": "TEST-USDT",
                "timeframe": "1h",
                "market_data": source.data,
                "metadata": source.metadata,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "buy"
    for output in body["outputs"]:
        if output["engine_name"] in CONTEXTUAL:
            assert all(item["bias"] is None for item in output["evidence"])
    confidence = next(o for o in body["outputs"] if o["engine_name"] == "confidence")
    assert confidence["data"]["independent_families"] == 5
