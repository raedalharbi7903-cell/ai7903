"""Closed-prefix advanced observations; never provider or order-book claims."""

from dataclasses import asdict, dataclass
from math import isfinite

from app.analysis.models import Candle

Finding = tuple[str, str | None, dict[str, object]]
Pivot = tuple[int, str, float]


def _integer(value: int, minimum: int, name: str) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _number(value: float, minimum: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{name} must be numeric")
    if not isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")


@dataclass(frozen=True)
class DivergenceConfig:
    left_window: int = 1
    right_window: int = 1
    minimum_separation: int = 1
    alignment_tolerance: int = 1
    minimum_magnitude: float = 0.0
    lookback: int = 128

    def __post_init__(self) -> None:
        for name in ("left_window", "right_window", "minimum_separation"):
            _integer(getattr(self, name), 1, name)
        _integer(self.alignment_tolerance, 0, "alignment_tolerance")
        _integer(self.lookback, 8, "lookback")
        _number(self.minimum_magnitude, 0, "minimum_magnitude")


@dataclass(frozen=True)
class VolumeConfig:
    baseline_window: int = 5
    high_threshold: float = 1.5
    low_threshold: float = 0.5

    def __post_init__(self) -> None:
        _integer(self.baseline_window, 2, "baseline_window")
        _number(self.high_threshold, 1, "high_threshold")
        _number(self.low_threshold, 0, "low_threshold")
        if not self.low_threshold < 1 < self.high_threshold:
            raise ValueError("Volume thresholds must straddle one")


@dataclass(frozen=True)
class SweepConfig:
    lookback: int = 5
    breach_tolerance: float = 0.0
    confirmation_candles: int = 1

    def __post_init__(self) -> None:
        _integer(self.lookback, 2, "lookback")
        _integer(self.confirmation_candles, 1, "confirmation_candles")
        _number(self.breach_tolerance, 0, "breach_tolerance")


@dataclass(frozen=True)
class StructureConfig:
    left_window: int = 1
    right_window: int = 1
    confirmation_candles: int = 2
    lookback: int = 128

    def __post_init__(self) -> None:
        _integer(self.left_window, 1, "left_window")
        _integer(self.right_window, 1, "right_window")
        _integer(self.confirmation_candles, 2, "confirmation_candles")
        _integer(self.lookback, 6, "lookback")


def closed_prefix(candles: list[Candle]) -> list[Candle]:
    """Do not bridge an incomplete candle with later observations."""
    for index, candle in enumerate(candles):
        if not candle.complete:
            return candles[:index]
    return candles


def confirmed_pivots(values: list[float], left: int = 1, right: int = 1) -> list[Pivot]:
    """First point of a plateau owns the pivot after right-window confirmation."""
    _integer(left, 1, "left")
    _integer(right, 1, "right")
    if not all(isfinite(value) for value in values):
        raise ValueError("Pivot values must be finite")
    pivots: list[Pivot] = []
    for index in range(left, len(values) - right):
        before = values[index - left : index]
        after = values[index + 1 : index + right + 1]
        if values[index] < min(before) and values[index] <= min(after):
            pivots.append((index, "low", values[index]))
        elif values[index] > max(before) and values[index] >= max(after):
            pivots.append((index, "high", values[index]))
    return pivots


def divergence(candles: list[Candle], config: DivergenceConfig) -> Finding:
    candles = closed_prefix(candles)
    details: dict[str, object] = {
        "sample_size": len(candles),
        "configuration": asdict(config),
        "confirmation_windows": {
            "left": config.left_window,
            "right": config.right_window,
        },
        "momentum_method": "one_period_close_difference",
        "price_method": "confirmed_close_swings",
    }
    if len(candles) < 8:
        return "insufficient_evidence", None, details
    values = [c.close for c in candles]
    price = confirmed_pivots(values, config.left_window, config.right_window)
    momentum = [
        (index + 1, kind, value)
        for index, kind, value in confirmed_pivots(
            [b - a for a, b in zip(values, values[1:], strict=False)],
            config.left_window,
            config.right_window,
        )
    ]
    start = max(0, len(candles) - config.lookback)
    # Wait for the entire alignment window. Otherwise a later, closer momentum
    # pivot could change an already emitted pair (repainting).
    matched: list[tuple[Pivot, Pivot]] = []
    used: set[int] = set()
    for pivot in price:
        index, kind, _ = pivot
        if index + config.alignment_tolerance + config.right_window >= len(candles):
            continue
        candidates = [
            item
            for item in momentum
            if item[1] == kind
            and abs(item[0] - index) <= config.alignment_tolerance
            and item[0] not in used
        ]
        if candidates:
            selected = min(candidates, key=lambda item: (abs(item[0] - index), item[0]))
            matched.append((pivot, selected))
            used.add(selected[0])
    # Preserve matching assignments even when an older pivot leaves the reporting
    # lookback. Dropping it before matching would allow reuse and change history.
    matched = [pair for pair in matched if pair[0][0] >= start]
    details["price_pivots"] = [item for item in price if item[0] >= start]
    details["momentum_pivots"] = [item for item in momentum if item[0] >= start]
    details["matched_pivots"] = [
        {
            "kind": p[1],
            "price_index": p[0],
            "price_value": p[2],
            "momentum_index": m[0],
            "momentum_value": m[2],
            "timestamp": candles[p[0]].timestamp.isoformat(),
            "confirmed_at": candles[
                p[0] + config.alignment_tolerance + config.right_window
            ].timestamp.isoformat(),
        }
        for p, m in matched
    ]
    candidates: list[tuple[int, str, str]] = []
    comparisons = 0
    for kind in ("low", "high"):
        same_kind = [pair for pair in matched if pair[0][1] == kind]
        if len(same_kind) < 2:
            continue
        latest = same_kind[-1]
        earlier = [
            pair
            for pair in same_kind[:-1]
            if latest[0][0] - pair[0][0] >= config.minimum_separation
        ]
        if not earlier:
            continue
        previous = earlier[-1]
        comparisons += 1
        price_change = latest[0][2] - previous[0][2]
        momentum_change = latest[1][2] - previous[1][2]
        if (
            abs(momentum_change) <= config.minimum_magnitude
            or price_change * momentum_change >= 0
        ):
            continue
        regular = (kind == "low" and price_change < 0) or (
            kind == "high" and price_change > 0
        )
        direction = "bullish" if kind == "low" else "bearish"
        state = f"{'regular' if regular else 'hidden'}_{direction}_divergence"
        candidates.append((latest[0][0], state, direction))
    if candidates:
        _, state, direction = max(candidates)
        return state, direction, details
    return (
        "no_divergence" if comparisons else "insufficient_evidence",
        None,
        details,
    )


def volume_anomaly(candles: list[Candle], config: VolumeConfig) -> Finding:
    candles = closed_prefix(candles)
    details: dict[str, object] = {"configuration": asdict(config)}
    window = candles[-(config.baseline_window + 1) :]
    if len(window) <= config.baseline_window:
        return "insufficient_volume_history", None, details
    volumes = [c.volume for c in window]
    if any(value is None for value in volumes):
        return "missing_volume", None, details
    values = [value for value in volumes if value is not None]
    if any(not isfinite(value) or value < 0 for value in values):
        return "invalid_volume", None, details
    baseline = sum(value / config.baseline_window for value in values[:-1])
    details.update(
        baseline=baseline,
        baseline_start=window[0].timestamp.isoformat(),
        baseline_end=window[-2].timestamp.isoformat(),
        current_volume=values[-1],
    )
    if baseline == 0:
        return "insufficient_volume_baseline", None, details
    relative = values[-1] / baseline
    if not isfinite(relative):
        return "invalid_volume", None, details
    state = (
        "high_relative_volume"
        if relative >= config.high_threshold
        else (
            "low_relative_volume"
            if relative <= config.low_threshold
            else "normal_volume"
        )
    )
    details.update(
        relative_volume=relative,
        activity=(
            "expansion" if relative > 1 else "contraction" if relative < 1 else "stable"
        ),
        scope="exchange_specific",
    )
    return state, None, details


def liquidity_sweep(candles: list[Candle], config: SweepConfig) -> Finding:
    candles = closed_prefix(candles)
    details: dict[str, object] = {
        "configuration": asdict(config),
        "inference": "ohlcv_only",
        "observed_orders": False,
    }
    if len(candles) < config.lookback + 1:
        return "insufficient_evidence", None, details
    # Search only candidates whose rejection confirmation could end at this bar.
    for age in range(config.confirmation_candles, -1, -1):
        index = len(candles) - 1 - age
        if index < config.lookback:
            continue
        prior = candles[index - config.lookback : index]
        high, low = max(c.high for c in prior), min(c.low for c in prior)
        candle = candles[index]
        buy = candle.high > high + config.breach_tolerance and candle.close < high
        sell = candle.low < low - config.breach_tolerance and candle.close > low
        if not buy and not sell:
            continue
        details.update(
            reference_high=high,
            reference_low=low,
            breach_timestamp=candle.timestamp.isoformat(),
            reference_start=prior[0].timestamp.isoformat(),
            reference_end=prior[-1].timestamp.isoformat(),
        )
        if buy and sell:
            return "conflicting_sweep_inference", None, details
        side, bias, level = (
            ("buy", "bearish", high) if buy else ("sell", "bullish", low)
        )
        confirmations = candles[index + 1 :]
        rejected = all(
            c.close < level if buy else c.close > level for c in confirmations
        )
        if not rejected:
            continue
        details["reference_level"] = level
        confirmed = len(confirmations) == config.confirmation_candles
        details["confirmation_status"] = (
            "confirmed_rejection" if confirmed else "potential"
        )
        return (
            f"{'confirmed' if confirmed else 'potential'}_{side}_side_sweep",
            bias,
            details,
        )
    return "no_confirmed_sweep", None, details


def market_transition(candles: list[Candle], config: StructureConfig) -> Finding:
    candles = closed_prefix(candles)
    details: dict[str, object] = {
        "configuration": asdict(config),
        "confirmation_candles": config.confirmation_candles,
        "sample_size": len(candles),
    }
    if len(candles) < 6:
        return "insufficient_evidence", None, details
    history = candles[: -config.confirmation_candles]
    references: list[tuple[int, str, float]] = []
    for kind, values in (
        ("high", [c.high for c in history]),
        ("low", [c.low for c in history]),
    ):
        pivots = [
            p
            for p in confirmed_pivots(values, config.left_window, config.right_window)
            if p[1] == kind and p[0] >= len(candles) - config.lookback
        ]
        if pivots:
            references.append(pivots[-1])
    for index, kind, level in references:
        details[f"reference_{kind}"] = level
        details[f"reference_{kind}_timestamp"] = candles[index].timestamp.isoformat()
        streak = 0
        for position in range(index + config.right_window + 1, len(candles)):
            beyond = (
                candles[position].close > level
                if kind == "high"
                else candles[position].close < level
            )
            streak = streak + 1 if beyond else 0
            if streak == config.confirmation_candles:
                # A break is an event, not a label repeatedly emitted for a trend.
                if position == len(candles) - 1:
                    bias = "bullish" if kind == "high" else "bearish"
                    details["confirmed_at"] = candles[position].timestamp.isoformat()
                    return f"confirmed_{bias}_structure_break", bias, details
                break
    prior = candles[-4].close - candles[-6].close
    recent = candles[-1].close - candles[-3].close
    state = (
        "bullish_continuation"
        if prior > 0 and recent > 0
        else (
            "bearish_continuation"
            if prior < 0 and recent < 0
            else (
                "potential_bullish_transition"
                if prior < 0 < recent
                else "potential_bearish_transition" if prior > 0 > recent else "range"
            )
        )
    )
    details.update(prior_change=prior, recent_change=recent)
    bias = (
        "bullish" if "bullish" in state else "bearish" if "bearish" in state else None
    )
    return state, bias, details
