from math import sqrt

from app.analysis.models import Candle


def closes(candles: list[Candle]) -> list[float]:
    return [c.close for c in candles]


def sma(values: list[float], period: int) -> float | None:
    return sum(values[-period:]) / period if len(values) >= period else None


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))][-period:]
    gains = sum(change for change in changes if change > 0) / period
    losses = -sum(change for change in changes if change < 0) / period
    if losses == 0:
        return 100.0
    return 100 - 100 / (1 + gains / losses)


def atr(candles: list[Candle], period: int = 14) -> float | None:
    if len(candles) <= period:
        return None
    ranges = [
        max(
            c.high - c.low,
            abs(c.high - candles[i - 1].close),
            abs(c.low - candles[i - 1].close),
        )
        for i, c in enumerate(candles[1:], 1)
    ]
    return sum(ranges[-period:]) / period


def correlation(first: list[float], second: list[float]) -> float | None:
    if len(first) < 3 or len(first) != len(second):
        return None
    first_mean, second_mean = sum(first) / len(first), sum(second) / len(second)
    numerator = sum(
        (a - first_mean) * (b - second_mean) for a, b in zip(first, second, strict=True)
    )
    left = sqrt(sum((a - first_mean) ** 2 for a in first))
    right = sqrt(sum((b - second_mean) ** 2 for b in second))
    return numerator / (left * right) if left and right else None


def analyze(
    name: str, candles: list[Candle]
) -> tuple[str, str | None, dict[str, object]]:
    values = closes(candles)
    if len(values) < 5:
        return "insufficient history", None, {}
    change = values[-1] - values[0]
    bias = "bullish" if change > 0 else "bearish" if change < 0 else "neutral"
    recent_high, recent_low = max(c.high for c in candles[-5:]), min(
        c.low for c in candles[-5:]
    )
    if name == "market_structure":
        highs = [c.high for c in candles[-5:]]
        lows = [c.low for c in candles[-5:]]
        state = (
            "higher_high_higher_low"
            if highs[-1] > highs[0] and lows[-1] > lows[0]
            else (
                "lower_high_lower_low"
                if highs[-1] < highs[0] and lows[-1] < lows[0]
                else "range_or_transition"
            )
        )
        return (
            state,
            bias,
            {
                "swing_high": recent_high,
                "swing_low": recent_low,
                "invalidation": recent_low if bias == "bullish" else recent_high,
            },
        )
    if name == "trend":
        fast, slow = sma(values, 3), sma(values, 5)
        state = (
            "structured_trend"
            if fast is not None
            and slow is not None
            and ((fast > slow) == (bias == "bullish"))
            else "mixed_trend"
        )
        return (
            state,
            bias,
            {"fast_average": fast, "slow_average": slow, "price_change": change},
        )
    if name == "support_resistance":
        return (
            "recent_reaction_range",
            bias,
            {
                "support": recent_low,
                "resistance": recent_high,
                "proximity": min(
                    abs(values[-1] - recent_low), abs(recent_high - values[-1])
                ),
            },
        )
    if name == "supply_demand":
        return (
            "inferred_demand_zone" if bias == "bullish" else "inferred_supply_zone",
            bias,
            {
                "zone_low": recent_low,
                "zone_high": recent_high,
                "observation": "inferred_from_ohlcv",
            },
        )
    if name == "liquidity":
        equal_highs = sum(
            abs(candles[i].high - candles[i - 1].high) < 1e-9
            for i in range(1, len(candles))
        )
        return (
            "swing_liquidity",
            bias,
            {
                "equal_high_pairs": equal_highs,
                "swing_high": recent_high,
                "swing_low": recent_low,
            },
        )
    if name == "volume":
        volumes = [c.volume for c in candles if c.volume is not None]
        average = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else None
        state = (
            "volume_expansion"
            if average and volumes[-1] > average
            else "volume_contraction"
        )
        return (
            state,
            bias,
            {
                "last_volume": volumes[-1] if volumes else None,
                "average_volume": average,
                "scope": "exchange_specific",
            },
        )
    if name == "momentum":
        value = rsi(values)
        state = (
            "overextended"
            if value is not None and (value >= 70 or value <= 30)
            else "momentum_aligned"
        )
        return (
            state,
            bias,
            {"rsi": value, "roc": (values[-1] - values[-2]) / values[-2]},
        )
    if name == "volatility":
        value = atr(candles)
        return (
            "atr_observation",
            None,
            {"atr": value, "relative_atr": value / values[-1] if value else None},
        )
    if name == "pattern_recognition":
        body = abs(candles[-1].close - candles[-1].open)
        spread = candles[-1].high - candles[-1].low
        state = (
            "range_rejection"
            if spread and body / spread < 0.35
            else "no_defined_pattern"
        )
        return (
            state,
            bias if state != "no_defined_pattern" else None,
            {"invalidation": recent_low if bias == "bullish" else recent_high},
        )
    if name == "candlestick":
        previous, current = candles[-2], candles[-1]
        engulfing = (
            current.close > current.open
            and previous.close < previous.open
            and current.close >= previous.open
        )
        return (
            "bullish_engulfing" if engulfing else "contextual_candle",
            "bullish" if engulfing else bias,
            {"open": current.open, "close": current.close},
        )
    if name == "correlation":
        return (
            "correlation_not_available",
            None,
            {"sample_size": len(values), "reason": "benchmark_series_required"},
        )
    return "unknown", None, {}
