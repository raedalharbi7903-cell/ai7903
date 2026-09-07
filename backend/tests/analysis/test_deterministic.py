from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.deterministic import analyze, atr, closes, correlation, rsi
from app.analysis.models import Candle


def candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=i),
            open=100 + i,
            high=102 + i,
            low=99 + i,
            close=101 + i,
            volume=100 + i,
        )
        for i in range(20)
    ]


@pytest.mark.parametrize(
    "engine",
    [
        "market_structure",
        "trend",
        "support_resistance",
        "supply_demand",
        "liquidity",
        "volume",
        "momentum",
        "volatility",
        "pattern_recognition",
        "candlestick",
        "correlation",
    ],
)
def test_engines_derive_observation_from_candles(engine: str) -> None:
    observation, bias, values = analyze(engine, candles())
    assert observation
    assert values
    assert bias in {"bullish", "bearish", "neutral", None}


def test_indicator_calculations_require_history() -> None:
    assert rsi(closes(candles())) is not None
    assert atr(candles()) is not None
    assert correlation([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
