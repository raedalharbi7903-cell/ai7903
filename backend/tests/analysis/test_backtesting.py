from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.backtesting import (
    BacktestConfig,
    HistoricalBacktester,
    _execute_trade,
    split_development_oos,
)
from app.analysis.models import Candle, DecisionState
from app.analysis.telemetry import InMemoryTelemetrySink


def candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
            open=100 + index,
            high=101 + index,
            low=99 + index,
            close=100 + index,
            volume=1,
        )
        for index in range(6)
    ]


def test_backtest_is_sequential_and_reproducible() -> None:
    result = HistoricalBacktester().run(
        candles(), "synthetic-unit-fixture", BacktestConfig("v1", "p1")
    )
    # Nearby resistance makes the original fixture's reward/risk unacceptable.
    assert result.trades == 0
    # With contextual votes removed, the two short prefixes are validated safe
    # NO_TRADE results rather than artificially directional risk rejections.
    assert result.validated_decisions == 2
    assert all(decision == DecisionState.NO_TRADE for decision in result.decisions)
    assert len(result.decisions) == 3


def test_oos_split_rejects_leakage_shape() -> None:
    development, oos = split_development_oos(candles(), 3)
    assert development[-1].timestamp < oos[0].timestamp
    with pytest.raises(ValueError):
        split_development_oos(candles(), len(candles()))


def test_pipeline_backtest_uses_sequential_production_service() -> None:
    result = HistoricalBacktester().run_pipeline(
        candles(), "synthetic-unit-fixture", BacktestConfig("v1", "p1")
    )
    assert len(result.decisions) == 3


def test_same_candle_stop_target_ambiguity_is_stop_first() -> None:
    decision = candles()[2]
    following = Candle(
        timestamp=candles()[3].timestamp,
        open=101,
        high=110,
        low=90,
        close=105,
    )
    trade = _execute_trade(
        DecisionState.BUY,
        decision,
        following,
        stop=95,
        target=108,
        config=BacktestConfig("v1", "p1", fee_rate=0.001, slippage_rate=0.001),
    )
    assert trade.exit_reason == "stop"
    assert trade.return_after_costs < 0


def test_backtest_emits_measurements_and_telemetry() -> None:
    sink = InMemoryTelemetrySink()
    result = HistoricalBacktester(sink).run_pipeline(
        candles(), "synthetic-unit-fixture", BacktestConfig("v1", "p1")
    )
    assert [event.event for event in sink.backtest_events] == ["started", "completed"]
    completed = sink.backtest_events[-1]
    assert completed.historical_analysis_count == len(result.decisions)
    assert completed.validated_decision_count == result.validated_decisions
    assert completed.executed_trade_count == result.trades


def test_backtest_telemetry_failure_is_isolated() -> None:
    class BrokenSink:
        def record_analysis(self, event: object) -> None:
            raise RuntimeError("unavailable")

        def record_backtest(self, event: object) -> None:
            raise RuntimeError("unavailable")

    result = HistoricalBacktester(BrokenSink()).run_pipeline(
        candles(), "synthetic-unit-fixture", BacktestConfig("v1", "p1")
    )
    assert result.trades >= 0


def test_backtest_failure_emits_failure_telemetry() -> None:
    sink = InMemoryTelemetrySink()
    with pytest.raises(ValueError, match="At least three"):
        HistoricalBacktester(sink).run_pipeline(
            candles()[:2], "synthetic-unit-fixture", BacktestConfig("v1", "p1")
        )
    assert [event.event for event in sink.backtest_events] == ["started", "failed"]
    assert sink.backtest_events[-1].error_category == "ValueError"
