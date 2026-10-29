from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.deterministic import analyze, rsi
from app.analysis.freshness import FreshnessPolicy, assess_market_data
from app.analysis.models import FreshnessStatus
from app.analysis.service import AnalysisService
from tests.analysis.test_advanced_behavior import candles
from tests.analysis.test_decision_states import complete_input
from tests.analysis.test_freshness_telemetry import market_data


@pytest.mark.parametrize("missing_index", [0, 3, 5])
def test_volume_never_reuses_an_older_sample_as_current(missing_index) -> None:
    data = candles([10, 11, 12, 13, 14, 15])
    data[missing_index].volume = None
    state, bias, _ = analyze("volume", data)
    assert state == "missing_volume"
    assert bias is None


def test_zero_volume_baseline_is_not_directional_contraction() -> None:
    data = candles([10, 11, 12, 13, 14, 15], volume=0)
    state, bias, _ = analyze("volume", data)
    assert state == "insufficient_volume_baseline"
    assert bias is None


def test_incomplete_tail_cannot_refresh_stale_closed_history() -> None:
    now = datetime(2026, 1, 2, tzinfo=UTC)
    data = market_data(now, complete=False)
    data.candles[0].timestamp = now - timedelta(hours=10)
    result = assess_market_data(data, now, FreshnessPolicy())
    assert result.status == FreshnessStatus.STALE
    assert result.completed_candle_timestamp == data.candles[0].timestamp


def test_only_incomplete_data_is_missing_not_delayed() -> None:
    now = datetime(2026, 1, 2, tzinfo=UTC)
    data = market_data(now, complete=False)
    data.candles = data.candles[-1:]
    assert (
        assess_market_data(data, now, FreshnessPolicy()).status
        == FreshnessStatus.MISSING
    )


def test_naive_reference_is_invalid_not_an_exception() -> None:
    data = market_data(datetime(2026, 1, 2, tzinfo=UTC))
    assert assess_market_data(data, datetime(2026, 1, 2), FreshnessPolicy()).status == (
        FreshnessStatus.INVALID
    )


def test_incomplete_middle_candle_invalidates_history() -> None:
    data = market_data(datetime(2026, 1, 2, tzinfo=UTC))
    data.candles[0].complete = False
    assert assess_market_data(
        data, data.source_timestamp, FreshnessPolicy()
    ).reason == ("incomplete_history")


@pytest.mark.parametrize(
    "config",
    [
        {"delayed_after_intervals": -1},
        {"delayed_after_intervals": 4, "stale_after_intervals": 3},
        {"delayed_after_intervals": True},
        {"timeframe_seconds": {"1h": 0}},
        {"timeframe_seconds": {"1h": -60}},
    ],
)
def test_invalid_freshness_policy_is_rejected(config) -> None:
    with pytest.raises(ValueError):
        FreshnessPolicy(**config)


def test_stale_closed_prefix_with_recent_incomplete_tail_is_not_actionable() -> None:
    source = complete_input()
    source.data["candles"][-1]["timestamp"] = "2026-01-02T00:00:00Z"
    source.data["candles"][-1]["complete"] = False
    result = AnalysisService().analyze(source)
    assert result.decision.value not in {"buy", "sell", "wait"}
    assert result.validation.value == "fail"


def test_rsi_flat_market_is_neutral_not_overbought() -> None:
    assert rsi([100] * 15) == 50
    assert rsi(list(range(1, 16))) == 100
    assert rsi(list(range(15, 0, -1))) == 0
