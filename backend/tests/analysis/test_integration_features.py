import pytest

from app.analysis.context import AnalysisContext
from app.analysis.engines import (
    ConfluenceEngine,
    CorrelationEngine,
    MultiTimeframeEngine,
    RiskEngine,
)
from app.analysis.models import (
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    Evidence,
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
    for candle in bearish["candles"]:
        candle["close"] = 24 - candle["close"]
        candle["open"] = 24 - candle["open"]
        candle["high"] = max(candle["open"], candle["close"]) + 1
        candle["low"] = min(candle["open"], candle["close"]) - 1
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


def test_risk_rejects_stop_too_tight_for_observed_volatility() -> None:
    source = fixture_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    context.add_output(
        EngineOutput(
            engine_name="market_structure",
            status=EngineLifecycleStatus.COMPLETED,
            data={"invalidation": 13.5},
        )
    )
    context.add_output(
        EngineOutput(
            engine_name="volatility",
            status=EngineLifecycleStatus.COMPLETED,
            data={"atr": 4.0, "relative_atr": 0.25},
        )
    )
    context.state["decision"] = DecisionState.BUY
    result = RiskEngine().analyze(context)
    assert result.status == EngineLifecycleStatus.FAILED
    assert "too tight" in result.warnings[0]


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
    assert "freshness is invalid" in result.warnings[0]


def test_mtf_rejects_stale_timeframe() -> None:
    source = fixture_input()
    stale = fixture_input().data
    stale["candles"] = stale["candles"][:1]
    source.metadata["timeframes"] = {
        "htf": stale,
        "itf": source.data,
        "ltf": source.data,
    }
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    result = MultiTimeframeEngine().analyze(context)
    assert result.status == EngineLifecycleStatus.DEGRADED
    assert result.data["freshness"] == "stale"


def test_same_family_conflict_does_not_inflate_confluence() -> None:
    source = fixture_input()
    data = MarketData.model_validate(source.data)
    context = AnalysisContext(source, market_data=data)
    for evidence_id, bias in (("momentum-a", "bullish"), ("momentum-b", "bearish")):
        context.evidence.append(
            Evidence(
                evidence_id=evidence_id,
                source_engine="momentum",
                family="momentum",
                instrument=data.instrument,
                market=data.market,
                timeframe=data.timeframe,
                timestamp=data.candles[-1].timestamp,
                finding="test",
                bias=bias,
            )
        )
    result = ConfluenceEngine().analyze(context)
    assert result.data["families"] == 1
    assert result.data["conflicted_families"] == ["momentum"]
    assert result.data["aligned"] is False
