"""Offline deterministic fixtures; no fitted model or financial efficacy claim."""

from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.analysis.backtesting import BacktestConfig, HistoricalBacktester
from app.analysis.models import Candle, MarketData
from app.analysis.service import AnalysisService
from app.analysis.telemetry import InMemoryTelemetrySink
from app.analysis.walk_forward import (
    WalkForwardConfig,
    WalkForwardEvaluator,
    build_folds,
)
from tests.analysis.test_decision_states import complete_input
from tests.analysis.test_pipeline import timeframe_fixtures


def candles(length=16):
    return [
        Candle(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
            open=100 + index,
            high=102 + index,
            low=99 + index,
            close=101 + index,
            volume=100,
        )
        for index in range(length)
    ]


def configuration(**changes):
    return WalkForwardConfig(
        **{
            "version": "synthetic-fold-v1",
            "training_size": 4,
            "test_size": 4,
            "window": "expanding",
            **changes,
        }
    )


def run(source=None, config=None, **kwargs):
    return WalkForwardEvaluator().run(
        candles() if source is None else source,
        "synthetic-walk-forward",
        "synthetic-data-v1",
        config or configuration(),
        BacktestConfig("strategy-fixed-v1", "parameters-fixed-v1"),
        **kwargs,
    )


@pytest.mark.parametrize("window", ["rolling", "expanding"])
def test_nonoverlapping_half_open_folds_have_explicit_gap(window):
    folds = build_folds(18, configuration(window=window, gap_size=2))
    assert [(f.train_end, f.test_start, f.test_end) for f in folds] == [
        (4, 6, 10),
        (8, 10, 14),
        (12, 14, 18),
    ]
    assert [f.train_start for f in folds] == (
        [0, 4, 8] if window == "rolling" else [0, 0, 0]
    )
    for previous, following in zip(folds, folds[1:], strict=False):
        assert previous.test_end <= following.test_start
        assert previous.train_end < previous.test_start


def test_partial_fold_policy_is_explicit_and_one_outcome_only_remainder_is_dropped():
    assert len(build_folds(15, configuration())) == 2
    folded = build_folds(15, configuration(include_partial=True))
    assert len(folded) == 3
    assert folded[-1].partial is True
    assert (folded[-1].test_start, folded[-1].test_end) == (12, 15)
    assert len(build_folds(13, configuration(include_partial=True))) == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"version": ""},
        {"version": True},
        {"training_size": True},
        {"training_size": 2},
        {"training_size": 3.0},
        {"test_size": True},
        {"test_size": 1},
        {"test_size": 0},
        {"gap_size": True},
        {"gap_size": -1},
        {"window": "invented"},
        {"window": []},
        {"include_partial": 1},
    ],
)
def test_invalid_configurations_are_not_coerced(changes):
    with pytest.raises(ValueError):
        configuration(**changes)


@pytest.mark.parametrize("length", [True, -1, 4.0, 0, 3, 5])
def test_invalid_or_insufficient_fold_history_is_explicit(length):
    with pytest.raises(ValueError):
        build_folds(length, configuration())


def test_tampered_frozen_configuration_is_revalidated_before_split():
    config = configuration()
    object.__setattr__(config, "test_size", 0)
    with pytest.raises(ValueError):
        build_folds(20, config)


@pytest.mark.parametrize("source", [[], [None], [True], ["not-a-candle"]])
def test_missing_or_wrong_typed_observations_fail_explicitly(source):
    with pytest.raises(ValueError, match="candles"):
        run(source)


@pytest.mark.parametrize(
    "start,end", [(True, None), (2, True), (1, None), (2, 100), (5, 4), (-1, 4)]
)
def test_backtester_rejects_invalid_explicit_decision_bounds(start, end):
    with pytest.raises(ValueError, match="bounds"):
        HistoricalBacktester().run_pipeline(
            candles(8),
            "synthetic",
            BacktestConfig("s1", "p1"),
            decision_start_index=start,
            decision_end_index=end,
        )


def test_default_backtester_behavior_is_unchanged_by_optional_bounds():
    source = candles(8)
    evaluator = HistoricalBacktester()
    config = BacktestConfig("s1", "p1")
    assert evaluator.run_pipeline(source, "synthetic", config) == (
        evaluator.run_pipeline(
            source,
            "synthetic",
            config,
            decision_start_index=2,
            decision_end_index=7,
        )
    )


@pytest.mark.parametrize("window", ["expanding", "rolling"])
def test_folds_execute_only_test_decisions_with_actual_point_in_time_service(
    monkeypatch, window
):
    source = candles()
    frame = MarketData(
        instrument="synthetic-benchmark",
        market="crypto",
        timeframe="1h",
        provider="synthetic",
        fixture=True,
        source_timestamp=source[-1].timestamp,
        candles=candles(),
    )
    observed = []
    analyze = AnalysisService.analyze

    def inspect(self, payload):
        observed.append(deepcopy(payload))
        return analyze(self, payload)

    monkeypatch.setattr(AnalysisService, "analyze", inspect)
    result = run(
        source, configuration(window=window, gap_size=1), timeframes={"htf": frame}
    )
    expected = [
        (fold.fold.train_start, index)
        for fold in result.folds
        for index in range(fold.fold.test_start, fold.fold.test_end - 1)
    ]
    assert len(observed) == len(expected)
    for request, (warmup_start, decision_index) in zip(observed, expected, strict=True):
        stamp = source[decision_index].timestamp
        assert request.metadata["decision_timestamp"] == stamp
        assert request.data["candles"][0]["timestamp"] == source[warmup_start].timestamp
        assert request.data["candles"][-1]["timestamp"] == stamp
        assert all(c["timestamp"] <= stamp for c in request.data["candles"])
        for value in request.metadata["timeframes"].values():
            assert value["source_timestamp"] <= stamp
            assert all(c["timestamp"] <= stamp for c in value["candles"])
    for fold in result.folds:
        assert (
            len(fold.result.decisions) == fold.fold.test_end - fold.fold.test_start - 1
        )
        assert (
            fold.first_decision_timestamp
            == source[fold.fold.test_start].timestamp.isoformat()
        )
        assert (
            fold.last_decision_timestamp
            == source[fold.fold.test_end - 2].timestamp.isoformat()
        )
        assert (
            fold.last_outcome_timestamp
            == source[fold.fold.test_end - 1].timestamp.isoformat()
        )


def test_adding_future_candles_cannot_change_completed_fold_results_or_provenance():
    first = run(candles(12))
    later = run(candles(20))
    assert first.folds == later.folds[: len(first.folds)]


def test_warmup_trade_is_not_counted_as_test_performance():
    source = complete_input()
    source.data["market"] = "crypto"
    history = [Candle.model_validate(row) for row in source.data["candles"]]
    for index in range(3):
        history.append(
            Candle(
                timestamp=history[-1].timestamp + timedelta(hours=1),
                open=14 + index,
                high=16 + index,
                low=13 + index,
                close=15 + index,
                volume=150,
            )
        )
    frames = {
        name: MarketData.model_validate(data)
        for name, data in timeframe_fixtures(source.data).items()
    }
    execution = BacktestConfig("fixed-s1", "fixed-p1")
    baseline = HistoricalBacktester().run_pipeline(
        history, "synthetic", execution, timeframes=frames, instrument="TEST"
    )
    assert (
        baseline.trades_detail[0].analysis_timestamp == history[4].timestamp.isoformat()
    )
    assert baseline.trades > 0
    result = WalkForwardEvaluator().run(
        history,
        "synthetic",
        "v1",
        configuration(training_size=6, test_size=2),
        execution,
        timeframes=frames,
        instrument="TEST",
    )
    fold = result.folds[0]
    assert len(fold.result.decisions) == 1
    assert all(
        trade.analysis_timestamp >= fold.first_decision_timestamp
        and trade.exit_timestamp <= fold.last_outcome_timestamp
        for trade in fold.result.trades_detail
    )
    assert not any(
        trade.analysis_timestamp == history[4].timestamp.isoformat()
        for trade in fold.result.trades_detail
    )


def test_fixed_parameter_results_are_reproducible_and_never_claim_calibration():
    source = candles()
    original = deepcopy(source)
    result = run(source)
    assert result == run(source)
    assert source == original
    assert result.training_performed is False
    assert result.calibration_status == "uncalibrated"
    assert result.return_aggregation == "per_fold_sum_of_one_bar_spot_long_returns"
    assert all(
        f.result.parameter_version == "parameters-fixed-v1" for f in result.folds
    )
    assert all(len(f.primary_prefix_sha256) == 64 for f in result.folds)


@pytest.mark.parametrize(
    "bad", ["naive", "duplicate", "unsorted", "open", "nan", "boolean"]
)
def test_invalid_history_is_rejected_without_mutating_caller(bad):
    source = candles()
    if bad == "naive":
        source[2].timestamp = source[2].timestamp.replace(tzinfo=None)
    elif bad == "duplicate":
        source[2].timestamp = source[1].timestamp
    elif bad == "unsorted":
        source[1], source[2] = source[2], source[1]
    elif bad == "open":
        source[2].complete = False
    elif bad == "nan":
        source[2].close = float("nan")
    else:
        source[2] = source[2].model_copy(update={"close": True})
    before = [c.model_dump(warnings=False) for c in source]
    with pytest.raises(ValueError):
        run(source)
    assert [c.model_dump(warnings=False) for c in source] == before


def test_bad_auxiliary_provenance_is_not_accepted_as_historical_fixture():
    frame = MarketData(
        instrument="synthetic",
        market="crypto",
        timeframe="1h",
        provider="synthetic",
        fixture=False,
        source_timestamp=candles()[-1].timestamp,
        candles=candles(),
    )
    before = frame.model_dump()
    with pytest.raises(ValueError, match="fixtures"):
        run(timeframes={"htf": frame})
    assert frame.model_dump() == before


def test_existing_telemetry_is_reused_and_sink_failures_do_not_change_results():
    sink = InMemoryTelemetrySink()
    evaluator = WalkForwardEvaluator(sink)
    config = configuration()
    execution = BacktestConfig("strategy-fixed-v1", "parameters-fixed-v1")
    result = evaluator.run(
        candles(), "synthetic-walk-forward", "synthetic-data-v1", config, execution
    )
    assert [e.event for e in sink.backtest_events] == ["started", "completed"] * len(
        result.folds
    )

    class Broken:
        def record_analysis(self, event):
            raise RuntimeError("PRIVATE_SINK_FAILURE")

        def record_backtest(self, event):
            raise RuntimeError("PRIVATE_SINK_FAILURE")

    assert (
        WalkForwardEvaluator(Broken()).run(
            candles(), "synthetic-walk-forward", "synthetic-data-v1", config, execution
        )
        == result
    )


def test_boolean_execution_costs_and_missing_provenance_are_rejected():
    with pytest.raises(ValueError, match="booleans"):
        WalkForwardEvaluator().run(
            candles(),
            "synthetic",
            "v1",
            configuration(),
            BacktestConfig("s1", "p1", fee_rate=False),
        )
    with pytest.raises(ValueError, match="explicit"):
        WalkForwardEvaluator().run(
            candles(), "", "v1", configuration(), BacktestConfig("s1", "p1")
        )
    with pytest.raises(ValueError, match="finite"):
        execution = replace(BacktestConfig("s1", "p1"), fee_rate=float("nan"))
        WalkForwardEvaluator().run(
            candles(), "synthetic", "v1", configuration(), execution
        )
