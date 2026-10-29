from math import fsum, isfinite, sqrt

from app.analysis.advanced import (
    DivergenceConfig as DivergenceConfig,
)
from app.analysis.advanced import (
    StructureConfig,
    SweepConfig,
    VolumeConfig,
    closed_prefix,
    divergence,
    liquidity_sweep,
    market_transition,
    volume_anomaly,
)
from app.analysis.advanced import (
    confirmed_pivots as confirmed_pivots,
)
from app.analysis.models import Candle


def closes(candles: list[Candle]) -> list[float]:
    return [c.close for c in candles]


def _period(period: int) -> None:
    if type(period) is not int or period <= 0:
        raise ValueError("Period must be a positive integer")


def _finite(values: list[float]) -> None:
    if any(not isfinite(value) for value in values):
        raise ValueError("Numeric observations must be finite")


def sma(values: list[float], period: int) -> float | None:
    _period(period)
    _finite(values)
    return (
        fsum(value / period for value in values[-period:])
        if len(values) >= period
        else None
    )


def rsi(values: list[float], period: int = 14) -> float | None:
    _period(period)
    _finite(values)
    if len(values) <= period:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))][-period:]
    _finite(changes)
    gains = fsum(change / period for change in changes if change > 0)
    losses = -fsum(change / period for change in changes if change < 0)
    if losses == 0:
        return 100.0 if gains else 50.0
    scale = max(gains, losses)
    normalized_gain, normalized_loss = gains / scale, losses / scale
    return 100 * normalized_gain / (normalized_gain + normalized_loss)


def atr(candles: list[Candle], period: int = 14) -> float | None:
    _period(period)
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
    return sma(ranges, period)


def correlation(first: list[float], second: list[float]) -> float | None:
    if len(first) < 3 or len(first) != len(second):
        return None
    _finite(first)
    _finite(second)
    first_scale, second_scale = max(map(abs, first)), max(map(abs, second))
    if not first_scale or not second_scale:
        return None
    # Pearson correlation is scale invariant. Normalize before centering and
    # multiplying to avoid overflow/underflow on valid finite observations.
    first = [value / first_scale for value in first]
    second = [value / second_scale for value in second]
    first_mean = fsum(first) / len(first)
    second_mean = fsum(second) / len(second)
    numerator = fsum(
        (a - first_mean) * (b - second_mean) for a, b in zip(first, second, strict=True)
    )
    left = sqrt(fsum((a - first_mean) ** 2 for a in first))
    right = sqrt(fsum((b - second_mean) ** 2 for b in second))
    return max(-1.0, min(1.0, numerator / (left * right))) if left and right else None


def analyze(
    name: str, candles: list[Candle], configuration: dict[str, object] | None = None
) -> tuple[str, str | None, dict[str, object]]:
    candles = closed_prefix(candles)
    configuration = configuration or {}
    if name == "momentum_divergence":
        return divergence(candles, DivergenceConfig(**configuration))
    if name == "volume_anomaly":
        return volume_anomaly(candles, VolumeConfig(**configuration))
    if name == "liquidity_sweep":
        return liquidity_sweep(candles, SweepConfig(**configuration))
    if name == "market_transition":
        return market_transition(candles, StructureConfig(**configuration))
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
            None,
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
            None,
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
            None,
            {
                "equal_high_pairs": equal_highs,
                "swing_high": recent_high,
                "swing_low": recent_low,
            },
        )
    if name == "volume":
        state, _, measurements = volume_anomaly(candles, VolumeConfig())
        if state.startswith(("insufficient", "missing", "invalid")):
            return state, None, measurements
        activity = measurements["activity"]
        return (
            f"volume_{activity}",
            bias,
            {
                **measurements,
                "last_volume": candles[-1].volume,
                "average_volume": measurements["baseline"],
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
        bullish_engulfing = (
            current.close > current.open
            and previous.close < previous.open
            and current.close >= previous.open
            and current.open <= previous.close
        )
        bearish_engulfing = (
            current.close < current.open
            and previous.close > previous.open
            and current.close <= previous.open
            and current.open >= previous.close
        )
        body, spread = abs(current.close - current.open), current.high - current.low
        doji = spread > 0 and body / spread <= 0.1
        lower_wick = min(current.open, current.close) - current.low
        upper_wick = current.high - max(current.open, current.close)
        hammer = body > 0 and lower_wick >= body * 2 and upper_wick <= body
        shooting_star = body > 0 and upper_wick >= body * 2 and lower_wick <= body
        conflicting = (bullish_engulfing and shooting_star) or (
            bearish_engulfing and hammer
        )
        state = (
            "bullish_engulfing"
            if bullish_engulfing
            else (
                "bearish_engulfing"
                if bearish_engulfing
                else (
                    "hammer"
                    if hammer
                    else (
                        "shooting_star"
                        if shooting_star
                        else "doji" if doji else "neutral_candle"
                    )
                )
            )
        )
        if conflicting:
            state = "conflicting_evidence"
        candle_bias = (
            "bullish"
            if bullish_engulfing or hammer
            else "bearish" if bearish_engulfing or shooting_star else None
        )
        if conflicting or doji:
            candle_bias = None
        return (
            state,
            candle_bias,
            {
                "open": current.open,
                "close": current.close,
                "body": body,
                "spread": spread,
                "lower_wick": lower_wick,
                "upper_wick": upper_wick,
                "context": bias,
                "reversal_guaranteed": False,
            },
        )
    if name == "correlation":
        return (
            "correlation_not_available",
            None,
            {"sample_size": len(values), "reason": "benchmark_series_required"},
        )
    return "unknown", None, {}
