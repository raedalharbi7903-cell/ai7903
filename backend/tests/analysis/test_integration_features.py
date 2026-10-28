import pytest

from app.analysis.context import AnalysisContext
from app.analysis.engines import CorrelationEngine, MultiTimeframeEngine, RiskEngine
from app.analysis.models import (
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    MarketData,
)
from tests.analysis.test_pipeline import fixture_input


def test_correlation_uses_benchmark_history() -> None:
    source = fixture_input()
    source.metadata["benchmark_candles"] = source.data["candles"]
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    result = CorrelationEngine().analyze(context)
    assert result.data["coefficient"] == pytest.approx(1.0)


def test_multi_timeframe_detects_conflict() -> None:
    source = fixture_input()
    bearish = fixture_input().data
    bearish["timeframe"] = "itf"
    bearish["candles"] = list(reversed(bearish["candles"]))
    source.metadata["timeframes"] = {
        "htf": source.data,
        "itf": bearish,
        "ltf": source.data,
    }
    result = MultiTimeframeEngine().analyze(
        AnalysisContext(source, market_data=MarketData.model_validate(source.data))
    )
    assert result.data["alignment"] == "conflict"


def test_risk_derives_levels_from_structure() -> None:
    source = fixture_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    context.add_output(
        EngineOutput(
            engine_name="market_structure",
            status=EngineLifecycleStatus.COMPLETED,
            data={"invalidation": 10},
        )
    )
    context.state["decision"] = DecisionState.BUY
    result = RiskEngine().analyze(context)
    assert result.data["risk_reward"] == 2.0


def test_risk_rejects_directionally_invalid_buy_stop() -> None:
    source = fixture_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    context.add_output(
        EngineOutput(
            engine_name="market_structure",
            status=EngineLifecycleStatus.COMPLETED,
            data={"invalidation": 20},
        )
    )
    context.state["decision"] = DecisionState.BUY
    result = RiskEngine().analyze(context)
    assert result.status == EngineLifecycleStatus.FAILED


def test_mtf_rejects_future_completed_candle() -> None:
    source = fixture_input()
    future = fixture_input().data
    future["candles"][-1]["timestamp"] = "2026-01-02T00:00:00Z"
    source.metadata["timeframes"] = {
        "htf": future,
        "itf": source.data,
        "ltf": source.data,
    }
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    result = MultiTimeframeEngine().analyze(context)
    assert result.status == EngineLifecycleStatus.DEGRADED
    assert "after decision time" in result.warnings[0]
