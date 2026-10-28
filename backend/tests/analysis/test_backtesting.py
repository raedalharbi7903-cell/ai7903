from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.backtesting import (
    BacktestConfig,
    HistoricalBacktester,
    _execute_trade,
    split_development_oos,
)
from app.analysis.models import Candle, DecisionState


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
    assert result.trades == 1
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
