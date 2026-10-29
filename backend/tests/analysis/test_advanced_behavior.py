from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.advanced import DivergenceConfig, SweepConfig, VolumeConfig
from app.analysis.deterministic import analyze, confirmed_pivots
from app.analysis.models import AnalysisInput, Candle, EngineLifecycleStatus
from app.analysis.service import AnalysisService


def candles(values: list[float], volume: float | None = 100) -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
            open=value,
            high=value + 1,
            low=value - 1,
            close=value,
            volume=volume,
        )
        for index, value in enumerate(values)
    ]


DIVERGENCES = [
    ([14, 15, 10, 13, 12, 9, 12, 13, 14], "regular_bullish_divergence"),
    ([16, 15, 20, 17, 18, 21, 18, 17, 16], "regular_bearish_divergence"),
    ([12, 13, 10, 14, 17, 12, 15, 16, 17], "hidden_bullish_divergence"),
    ([18, 17, 20, 16, 13, 18, 15, 14, 13], "hidden_bearish_divergence"),
]


@pytest.mark.parametrize(("values", "expected"), DIVERGENCES)
def test_four_divergences_use_confirmed_matched_pivots(values, expected) -> None:
    state, bias, details = analyze("momentum_divergence", candles(values))
    assert state == expected
    assert bias in expected
    assert len(details["matched_pivots"]) >= 2
    for match in details["matched_pivots"]:
        assert abs(match["price_index"] - match["momentum_index"]) <= 1
        assert match["confirmed_at"] <= candles(values)[-1].timestamp.isoformat()


def test_absent_and_insufficient_divergence_are_distinct() -> None:
    assert (
        analyze("momentum_divergence", candles([1, 2, 3]))[0] == "insufficient_evidence"
    )
    data = candles([14, 15, 10, 13, 16, 9, 12, 13, 14])
    assert analyze("momentum_divergence", data)[0] == "no_divergence"


@pytest.mark.parametrize(
    "configuration",
    [
        {"minimum_separation": 8},
        {"minimum_magnitude": 2},
        {"left_window": 4},
        {"right_window": 4},
    ],
)
def test_divergence_settings_are_effective(configuration) -> None:
    data = candles(DIVERGENCES[0][0])
    assert analyze("momentum_divergence", data)[0] == DIVERGENCES[0][1]
    assert analyze("momentum_divergence", data, configuration)[0] != DIVERGENCES[0][1]


def test_alignment_tolerance_and_lookback_are_effective() -> None:
    data = candles([15, 16, 11, 10, 14, 17, 11, 10.5, 13, 14])
    assert analyze("momentum_divergence", data)[0] == "hidden_bullish_divergence"
    assert analyze("momentum_divergence", data, {"alignment_tolerance": 0})[0] != (
        "hidden_bullish_divergence"
    )
    data = candles(DIVERGENCES[0][0] + [15, 16, 17])
    assert analyze("momentum_divergence", data)[0] == DIVERGENCES[0][1]
    assert analyze("momentum_divergence", data, {"lookback": 8})[0] != DIVERGENCES[0][1]


@pytest.mark.parametrize(("values", "expected"), DIVERGENCES)
def test_confirmed_matches_do_not_repaint(values, expected) -> None:
    prefix = candles(values)
    original = analyze("momentum_divergence", prefix)
    extended = candles(values + [50, 1, 60, 2, 70])
    new = analyze("momentum_divergence", extended)
    for match in original[2]["matched_pivots"]:
        assert match in new[2]["matched_pivots"]
    assert analyze("momentum_divergence", extended[: len(prefix)]) == original
    unclosed = candles(values + [500])
    unclosed[-1].complete = False
    assert analyze("momentum_divergence", unclosed) == original


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True])
def test_invalid_magnitude_is_rejected(value) -> None:
    with pytest.raises(ValueError):
        DivergenceConfig(minimum_magnitude=value)


def test_pivot_plateaus_and_confirmation_boundaries() -> None:
    assert confirmed_pivots([10, 8, 8, 9]) == [(1, "low", 8)]
    assert confirmed_pivots([8, 10, 10, 9]) == [(1, "high", 10)]
    assert confirmed_pivots([10, 8, 9], right=2) == []
    with pytest.raises(ValueError):
        confirmed_pivots([1, 2, 3], left=0)


@pytest.mark.parametrize(
    ("last", "state", "activity"),
    [
        (150, "high_relative_volume", "expansion"),
        (50, "low_relative_volume", "contraction"),
        (100, "normal_volume", "stable"),
        (0, "low_relative_volume", "contraction"),
    ],
)
def test_volume_classification_excludes_current_bar(last, state, activity) -> None:
    data = candles([10] * 6)
    data[-1].volume = last
    result = analyze("volume_anomaly", data)
    assert result[0] == state
    assert result[2]["baseline"] == 100
    assert result[2]["activity"] == activity
    assert result[2]["baseline_end"] == data[-2].timestamp.isoformat()


@pytest.mark.parametrize(
    ("volumes", "expected"),
    [
        ([100, 100, 100, 100, 100, None], "missing_volume"),
        ([100, None, 100, 100, 100, 100], "missing_volume"),
        ([100, 100, 100, 100, 100, -1], "invalid_volume"),
        ([100, 100, 100, 100, 100, float("inf")], "invalid_volume"),
        ([0, 0, 0, 0, 0, 100], "insufficient_volume_baseline"),
    ],
)
def test_volume_invalid_missing_and_zero_baselines(volumes, expected) -> None:
    data = candles([10] * 6)
    for candle, volume in zip(data, volumes, strict=True):
        candle.volume = volume
    assert analyze("volume_anomaly", data)[0] == expected


def test_volume_configuration_and_outlier_isolation() -> None:
    data = candles([10] * 6)
    data[0].volume = 1000000
    data[-1].volume = 160
    config = {"baseline_window": 3, "high_threshold": 2, "low_threshold": 0.2}
    result = analyze("volume_anomaly", data, config)
    assert result[0] == "normal_volume"
    assert result[2]["baseline"] == 100
    with pytest.raises(ValueError):
        VolumeConfig(low_threshold=1.1)


@pytest.mark.parametrize("buy_side", [True, False])
def test_sweep_potential_then_confirmed_rejection(buy_side) -> None:
    data = candles([10] * 7)
    data[5].high = 12 if buy_side else 10.5
    data[5].low = 9.5 if buy_side else 8
    side = "buy" if buy_side else "sell"
    assert analyze("liquidity_sweep", data[:6])[0] == f"potential_{side}_side_sweep"
    result = analyze("liquidity_sweep", data)
    assert result[0] == f"confirmed_{side}_side_sweep"
    assert result[2]["reference_end"] == data[4].timestamp.isoformat()
    assert result[2]["inference"] == "ohlcv_only"
    assert result[2]["observed_orders"] is False
    data[6].close = 12 if buy_side else 8
    data[6].high = 13
    data[6].low = 7
    assert analyze("liquidity_sweep", data)[0] != f"confirmed_{side}_side_sweep"


def test_sweep_boundaries_conflict_and_tolerance() -> None:
    data = candles([10] * 6)
    assert analyze("liquidity_sweep", data)[0] == "no_confirmed_sweep"
    data[-1].high = 12
    assert analyze("liquidity_sweep", data, {"breach_tolerance": 1})[0] == (
        "no_confirmed_sweep"
    )
    data[-1].low = 8
    assert analyze("liquidity_sweep", data)[0] == "conflicting_sweep_inference"
    assert analyze("liquidity_sweep", data[:4])[0] == "insufficient_evidence"
    with pytest.raises(ValueError):
        SweepConfig(confirmation_candles=0)


def test_sweep_confirmation_rule_is_effective() -> None:
    data = candles([10] * 8)
    data[5].high = 12
    config = {"confirmation_candles": 2}
    assert analyze("liquidity_sweep", data[:7], config)[0] == "potential_buy_side_sweep"
    assert analyze("liquidity_sweep", data, config)[0] == "confirmed_buy_side_sweep"


@pytest.mark.parametrize(
    "engine",
    [
        "momentum_divergence",
        "liquidity_sweep",
        "volume_anomaly",
        "market_transition",
        "candlestick",
    ],
)
def test_all_advanced_engines_ignore_unclosed_tail_and_replay_prefix(engine) -> None:
    data = candles(DIVERGENCES[0][0])
    baseline = analyze(engine, data)
    future = candles(DIVERGENCES[0][0] + [1000, 1])
    assert analyze(engine, future[: len(data)]) == baseline
    future[len(data)].complete = False
    assert analyze(engine, future) == baseline


@pytest.mark.parametrize(("values", "expected"), DIVERGENCES)
def test_divergence_is_reached_and_configured_through_service(values, expected) -> None:
    data = candles(values)
    request = AnalysisInput(
        data={
            "instrument": "TEST-USDT",
            "market": "crypto",
            "timeframe": "1h",
            "provider": "synthetic-test",
            "fixture": True,
            "source_timestamp": data[-1].timestamp.isoformat(),
            "candles": [c.model_dump(mode="json") for c in data],
        }
    )
    result = AnalysisService().analyze(request)
    finding = next(
        f for f in result.advanced_findings if f.engine_id == "momentum_divergence"
    )
    assert finding.classification == expected
    assert finding.family == "momentum"
    request.metadata["engine_configuration"] = {
        "momentum_divergence": {"minimum_separation": 100}
    }
    result = AnalysisService().analyze(request)
    output = next(o for o in result.outputs if o.engine_name == "momentum_divergence")
    assert output.data["classification"] == "insufficient_evidence"
    assert output.status == EngineLifecycleStatus.DEGRADED
    assert not output.evidence


def test_engulfing_requires_both_body_boundaries_and_conflicts_are_neutral() -> None:
    data = candles([10] * 5)
    data[-2].open, data[-2].close = 11, 10
    data[-1].open, data[-1].close = 10.5, 11.5
    data[-1].high, data[-1].low = 12, 10
    assert analyze("candlestick", data)[0] != "bullish_engulfing"
    data[-1].open = 9.5
    data[-1].high = 16
    result = analyze("candlestick", data)
    assert result[0] == "conflicting_evidence"
    assert result[1] is None


@pytest.mark.parametrize("reflect", [False, True])
def test_structure_confirmation_event_is_not_repeated(reflect) -> None:
    values = [10, 11, 10, 11, 13, 15, 17]
    if reflect:
        values = [30 - value for value in values]
    data = candles(values)
    assert analyze("market_transition", data[:6])[0].startswith("confirmed_")
    assert not analyze("market_transition", data)[0].startswith("confirmed_")
    assert not analyze("market_transition", data[:5])[0].startswith("confirmed_")


@pytest.mark.parametrize("last", [11, 12])
def test_failed_break_or_equal_level_is_not_confirmed(last) -> None:
    data = candles([10, 11, 10, 11, 13, last])
    assert not analyze("market_transition", data)[0].startswith("confirmed_")


def test_structure_confirmation_configuration_and_unclosed_candle() -> None:
    data = candles([10, 11, 10, 11, 13, 15, 17])
    config = {"confirmation_candles": 3}
    assert not analyze("market_transition", data[:6], config)[0].startswith(
        "confirmed_"
    )
    assert analyze("market_transition", data, config)[0] == (
        "confirmed_bullish_structure_break"
    )
    data[-1].complete = False
    assert not analyze("market_transition", data, config)[0].startswith("confirmed_")
