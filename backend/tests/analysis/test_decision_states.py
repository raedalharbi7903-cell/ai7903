from copy import deepcopy

from app.analysis.context import AnalysisContext
from app.analysis.engines import BaseEngine, default_engines
from app.analysis.models import (
    AnalysisInput,
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    ValidationStatus,
)
from app.analysis.service import AnalysisService
from tests.analysis.test_pipeline import fixture_input, timeframe_fixtures


def complete_input() -> AnalysisInput:
    source = fixture_input()
    # A historical upper wick supplies a target beyond the structural stop distance.
    source.data["candles"][2]["high"] = 30
    source.metadata["timeframes"] = timeframe_fixtures(source.data)
    return source


def bearish_input() -> AnalysisInput:
    source = complete_input()
    bearish = deepcopy(source.data)
    for candle in bearish["candles"]:
        candle["open"] = 24 - candle["open"]
        candle["close"] = 24 - candle["close"]
        candle["high"] = max(candle["open"], candle["close"]) + 1
        candle["low"] = min(candle["open"], candle["close"]) - 1
    source.data = bearish
    # A real lower reference level is required; do not rely on target projection
    # to bypass a nearby structural target.
    bearish["candles"][2]["low"] = 1
    source.metadata["timeframes"] = timeframe_fixtures(bearish)
    return source


def test_production_pipeline_returns_buy_and_sell_when_validated() -> None:
    bullish = AnalysisService().analyze(complete_input())
    bearish = AnalysisService().analyze(bearish_input())
    assert bullish.decision == DecisionState.BUY
    assert bullish.validation == ValidationStatus.PASS
    assert bearish.decision == DecisionState.SELL
    assert bearish.validation == ValidationStatus.PASS


def test_production_pipeline_returns_no_trade_for_mtf_conflict() -> None:
    source = complete_input()
    source.metadata["timeframes"]["itf"] = bearish_input().data
    result = AnalysisService().analyze(source)
    assert result.decision == DecisionState.NO_TRADE
    assert result.validation == ValidationStatus.PASS


def test_production_pipeline_returns_wait_for_delayed_primary_data() -> None:
    source = complete_input()
    source.metadata["decision_timestamp"] = "2026-01-01T06:00:00Z"
    result = AnalysisService().analyze(source)
    assert result.decision == DecisionState.WAIT
    assert result.validation == ValidationStatus.PASS


def test_production_pipeline_returns_insufficient_data_for_missing_input() -> None:
    result = AnalysisService().analyze(AnalysisInput())
    assert result.decision == DecisionState.INSUFFICIENT_DATA
    assert result.validation == ValidationStatus.FAIL


def test_invalid_structural_risk_becomes_public_no_trade() -> None:
    class EqualStopStructure(BaseEngine):
        name, family = "market_structure", "structure"

        def analyze(self, context: AnalysisContext) -> EngineOutput:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.COMPLETED,
                data={"invalidation": 14},
            )

    engines = list(default_engines())
    index = next(
        position
        for position, engine in enumerate(engines)
        if engine.name == "market_structure"
    )
    engines[index] = EqualStopStructure()
    result = AnalysisService(engines=tuple(engines)).analyze(complete_input())
    validation = next(
        output for output in result.outputs if output.engine_name == "validation"
    )
    assert result.decision == DecisionState.NO_TRADE
    assert result.validation == ValidationStatus.FAIL
    assert "valid structural risk" in validation.data["reasons"][0]
