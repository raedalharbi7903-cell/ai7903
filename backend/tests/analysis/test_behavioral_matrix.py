from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.deterministic import analyze, correlation
from app.analysis.models import Candle


def series(values: list[float], volumes: list[float] | None = None) -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
            open=value - 0.25,
            high=value + 1,
            low=value - 1,
            close=value,
            volume=volumes[index] if volumes else 100,
        )
        for index, value in enumerate(values)
    ]


@pytest.mark.parametrize(
    ("values", "expected_bias"),
    [
        ([10, 11, 12, 13, 14, 15], "bullish"),
        ([15, 14, 13, 12, 11, 10], "bearish"),
        ([10, 10, 10, 10, 10, 10], "neutral"),
    ],
)
def test_structure_and_trend_cover_bullish_bearish_and_neutral_market(
    values: list[float], expected_bias: str
) -> None:
    for engine in ("market_structure", "trend"):
        _, bias, measurements = analyze(engine, series(values))
        assert bias == expected_bias
        assert measurements


def test_support_resistance_and_supply_demand_are_candle_derived() -> None:
    candles = series([10, 11, 12, 13, 14, 15])
    _, _, levels = analyze("support_resistance", candles)
    _, bias, zone = analyze("supply_demand", candles)
    assert levels["support"] < levels["resistance"]
    # CTO Option A: a range/zone observation is not an independent direction vote.
    assert bias is None
    assert zone["observation"] == "inferred_from_ohlcv"


def test_liquidity_and_volume_remain_ohlcv_context_not_order_book_claims() -> None:
    candles = series([10, 11, 12, 13, 14, 15], [10, 10, 10, 10, 10, 100])
    candles[3].high = candles[2].high
    _, _, liquidity = analyze("liquidity", candles)
    state, _, volume = analyze("volume", candles)
    assert liquidity["equal_high_pairs"] >= 1
    assert state == "volume_expansion"
    assert volume["scope"] == "exchange_specific"


def test_momentum_and_volatility_handle_history_boundaries() -> None:
    rising = series(list(range(10, 30)))
    _, positive, momentum = analyze("momentum", rising)
    _, _, volatility = analyze("volatility", rising)
    _, _, insufficient = analyze("volatility", series([10, 11, 12, 13, 14]))
    assert positive == "bullish"
    assert momentum["rsi"] is not None
    assert volatility["atr"] is not None
    assert insufficient["atr"] is None


def test_pattern_and_candlestick_supported_behavior() -> None:
    candles = series([10, 11, 12, 13, 14, 15])
    candles[-1].open = 14
    candles[-2].open = 15
    candles[-2].close = 14
    pattern, _, _ = analyze("pattern_recognition", candles)
    candlestick, bias, _ = analyze("candlestick", candles)
    assert pattern in {"range_rejection", "no_defined_pattern"}
    assert candlestick == "bullish_engulfing"
    assert bias == "bullish"


def test_correlation_covers_positive_negative_and_insufficient_overlap() -> None:
    assert correlation([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
    assert correlation([1, 2, 3], [6, 4, 2]) == pytest.approx(-1.0)
    assert correlation([1, 2], [2, 4]) is None
