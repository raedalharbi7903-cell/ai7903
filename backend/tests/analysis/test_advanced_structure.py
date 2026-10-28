from datetime import UTC, datetime, timedelta

from app.analysis.deterministic import analyze, confirmed_pivots
from app.analysis.models import Candle


def candles(closes: list[float]) -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
            open=value - 0.5,
            high=value + 1,
            low=value - 1,
            close=value,
        )
        for index, value in enumerate(closes)
    ]


def test_confirmed_bullish_break_requires_two_closed_candles() -> None:
    data = candles([10, 11, 10, 11, 13, 14])
    state, bias, details = analyze("market_transition", data)
    assert state == "confirmed_bullish_structure_break"
    assert bias == "bullish"
    assert details["confirmation_candles"] == 2
    assert details["reference_high"] == 12


def test_confirmed_bearish_break_requires_two_closed_candles() -> None:
    data = candles([14, 13, 14, 13, 11, 10])
    state, bias, details = analyze("market_transition", data)
    assert state == "confirmed_bearish_structure_break"
    assert bias == "bearish"
    assert details["reference_low"] == 12


def test_single_candle_break_is_not_confirmed_and_prefix_safe() -> None:
    partial = candles([10, 11, 10, 11, 13])
    state, _, _ = analyze("market_transition", partial)
    assert state != "confirmed_bullish_structure_break"
    full = candles([10, 11, 10, 11, 13, 14])
    assert analyze("market_transition", full)[0] == "confirmed_bullish_structure_break"


def test_transition_degrades_with_insufficient_history() -> None:
    state, bias, details = analyze("market_transition", candles([10, 11, 12, 13, 14]))
    assert state == "insufficient_evidence"
    assert bias is None
    assert details["sample_size"] == 5


def test_pivots_require_right_side_confirmation_without_future_access() -> None:
    prefix = [10, 8, 9]
    assert confirmed_pivots(prefix) == [(1, "low", 8)]
    assert confirmed_pivots([10, 8]) == []
