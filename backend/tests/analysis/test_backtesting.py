from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.backtesting import (
    BacktestConfig,
    HistoricalBacktester,
    split_development_oos,
)
from app.analysis.models import Candle


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
    assert result.trades == 4
    assert len(result.decisions) == 4


def test_oos_split_rejects_leakage_shape() -> None:
    development, oos = split_development_oos(candles(), 3)
    assert development[-1].timestamp < oos[0].timestamp
    with pytest.raises(ValueError):
        split_development_oos(candles(), len(candles()))
