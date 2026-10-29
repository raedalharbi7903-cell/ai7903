"""Timeframe-aware data freshness assessment for deterministic analysis."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.analysis.models import Candle, FreshnessStatus, MarketData

TIMEFRAME_SECONDS: dict[str, int] = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "fixture": 3600,
}


@dataclass(frozen=True)
class FreshnessPolicy:
    """Explicit, configurable tolerance expressed in completed candle intervals."""

    delayed_after_intervals: int = 1
    stale_after_intervals: int = 3
    timeframe_seconds: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if (
            type(self.delayed_after_intervals) is not int
            or type(self.stale_after_intervals) is not int
            or not 0 <= self.delayed_after_intervals <= self.stale_after_intervals
        ):
            raise ValueError("Freshness intervals must be ordered nonnegative integers")
        if self.timeframe_seconds is not None and any(
            type(seconds) is not int or seconds <= 0
            for seconds in self.timeframe_seconds.values()
        ):
            raise ValueError("Timeframe durations must be positive integer seconds")

    def interval_for(self, timeframe: str) -> timedelta | None:
        values = self.timeframe_seconds or TIMEFRAME_SECONDS
        seconds = values.get(timeframe)
        return timedelta(seconds=seconds) if seconds else None


@dataclass(frozen=True)
class FreshnessResult:
    status: FreshnessStatus
    reason: str
    reference_timestamp: datetime
    completed_candle_timestamp: datetime | None


def assess_market_data(
    data: MarketData,
    reference_timestamp: datetime,
    policy: FreshnessPolicy,
) -> FreshnessResult:
    return assess_candles(
        data.candles,
        data.timeframe,
        reference_timestamp,
        policy,
    )


def assess_candles(
    candles: list[Candle],
    timeframe: str,
    reference_timestamp: datetime,
    policy: FreshnessPolicy,
) -> FreshnessResult:
    if not candles:
        return FreshnessResult(
            FreshnessStatus.MISSING, "missing_candles", reference_timestamp, None
        )
    if reference_timestamp.tzinfo is None or any(
        candle.timestamp.tzinfo is None for candle in candles
    ):
        return FreshnessResult(
            FreshnessStatus.INVALID, "naive_timestamp", reference_timestamp, None
        )
    if any(
        later.timestamp <= earlier.timestamp
        for earlier, later in zip(candles, candles[1:], strict=False)
    ):
        return FreshnessResult(
            FreshnessStatus.INVALID,
            "non_monotonic_timestamps",
            reference_timestamp,
            None,
        )
    if any(not candle.complete for candle in candles[:-1]):
        return FreshnessResult(
            FreshnessStatus.INVALID, "incomplete_history", reference_timestamp, None
        )
    incomplete_tail = not candles[-1].complete
    completed = candles[-2] if incomplete_tail and len(candles) > 1 else candles[-1]
    if not completed.complete:
        return FreshnessResult(
            FreshnessStatus.MISSING,
            "no_completed_candle",
            reference_timestamp,
            None,
        )
    if completed.timestamp > reference_timestamp:
        return FreshnessResult(
            FreshnessStatus.INVALID,
            "future_completed_candle",
            reference_timestamp,
            completed.timestamp,
        )
    interval = policy.interval_for(timeframe)
    if interval is None:
        return FreshnessResult(
            FreshnessStatus.INVALID,
            "unknown_timeframe_policy",
            reference_timestamp,
            completed.timestamp,
        )
    age = reference_timestamp - completed.timestamp
    if age <= interval * policy.delayed_after_intervals:
        status, reason = FreshnessStatus.FRESH, "within_freshness_window"
    elif age <= interval * policy.stale_after_intervals:
        status, reason = FreshnessStatus.DELAYED, "within_delay_window"
    else:
        status, reason = FreshnessStatus.STALE, "outside_staleness_window"
    if incomplete_tail and status == FreshnessStatus.FRESH:
        status, reason = FreshnessStatus.DELAYED, "incomplete_latest_candle"
    return FreshnessResult(status, reason, reference_timestamp, completed.timestamp)
