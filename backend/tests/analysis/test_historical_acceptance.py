from datetime import timedelta

import pytest

from app.analysis.backtesting import (
    BacktestConfig,
    HistoricalBacktester,
    _execute_trade,
    _visible_frames,
    split_development_oos,
)
from app.analysis.context import AnalysisContext
from app.analysis.engines import MultiTimeframeEngine
from app.analysis.models import Candle, DecisionState, EngineLifecycleStatus, MarketData
from app.analysis.service import AnalysisService
from tests.analysis.test_backtesting import candles
from tests.analysis.test_decision_states import complete_input
from tests.analysis.test_pipeline import fixture_input, timeframe_fixtures


def test_backtest_uses_true_asof_frames_not_three_copies(monkeypatch) -> None:
    observed = []
    original = AnalysisService.analyze

    def inspect(self, request):
        observed.append(request)
        return original(self, request)

    monkeypatch.setattr(AnalysisService, "analyze", inspect)
    result = HistoricalBacktester().run(
        candles(), "synthetic", BacktestConfig("v1", "p1")
    )
    assert result.trades == 0
    assert all(request.metadata["timeframes"] == {} for request in observed)
    for index, request in enumerate(observed, 2):
        assert len(request.data["candles"]) == index + 1
        assert request.data["candles"][-1]["timestamp"] == candles()[index].timestamp


def test_historical_frame_snapshots_exclude_future_and_incomplete_data() -> None:
    source = fixture_input().data
    frames = {
        role: MarketData.model_validate(data)
        for role, data in timeframe_fixtures(source).items()
    }
    decision = frames["itf"].candles[2]
    snapshots = _visible_frames(frames, decision)
    for frame in snapshots.values():
        assert all(c["timestamp"] <= decision.timestamp for c in frame["candles"])
    frames["htf"].candles[1].complete = False
    assert len(_visible_frames(frames, decision)["htf"]["candles"]) == 1


def test_mtf_rejects_relabelled_primary_copies_and_bad_cadence() -> None:
    source = fixture_input()
    source.metadata["timeframes"] = {
        role: source.data for role in ("htf", "itf", "ltf")
    }
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    output = MultiTimeframeEngine().analyze(context)
    assert output.status == EngineLifecycleStatus.DEGRADED
    assert "distinct ordered" in output.warnings[0]
    frames = timeframe_fixtures(source.data)
    frames["htf"]["timeframe"] = "1d"
    source.metadata["timeframes"] = frames
    output = MultiTimeframeEngine().analyze(context)
    assert output.status == EngineLifecycleStatus.DEGRADED
    assert "intervals" in output.warnings[0]


@pytest.mark.parametrize("field", ["fee_rate", "slippage_rate"])
@pytest.mark.parametrize("value", [-0.1, 1, float("nan"), float("inf")])
def test_invalid_execution_costs_are_rejected(field, value) -> None:
    with pytest.raises(ValueError):
        BacktestConfig("v1", "p1", **{field: value})


def test_unsupported_execution_assumptions_are_not_silently_ignored() -> None:
    with pytest.raises(ValueError):
        BacktestConfig("v1", "p1", entry_timing="next_open")
    with pytest.raises(ValueError):
        BacktestConfig("v1", "p1", same_candle_policy="target_first")


def test_gap_stop_and_both_sided_costs_are_conservative() -> None:
    decision = candles()[0]
    execution = Candle(
        timestamp=decision.timestamp + timedelta(hours=1),
        open=90,
        high=120,
        low=80,
        close=110,
    )
    trade = _execute_trade(
        DecisionState.BUY,
        decision,
        execution,
        95,
        115,
        BacktestConfig("v1", "p1", fee_rate=0.01, slippage_rate=0.01),
    )
    assert trade.entry_price == 101
    assert trade.exit_price == pytest.approx(89.1)
    assert trade.exit_reason == "stop"
    assert trade.return_after_costs == pytest.approx((89.1 * 0.99 - 101 * 1.01) / 101)


def test_spot_backtester_never_opens_short_position() -> None:
    with pytest.raises(ValueError, match="short"):
        _execute_trade(
            DecisionState.SELL,
            candles()[0],
            candles()[1],
            105,
            95,
            BacktestConfig("v1", "p1"),
        )


def test_slippage_cannot_turn_target_into_invalid_geometry() -> None:
    with pytest.raises(ValueError, match="geometry"):
        _execute_trade(
            DecisionState.BUY,
            candles()[0],
            candles()[1],
            95,
            101,
            BacktestConfig("v1", "p1", slippage_rate=0.02),
        )


def test_oos_split_rejects_overlapping_or_unsorted_timestamps() -> None:
    data = candles()
    data[3].timestamp = data[2].timestamp
    with pytest.raises(ValueError, match="chronological"):
        split_development_oos(data, 3)


def test_backtest_is_reproducible_and_records_policy() -> None:
    config = BacktestConfig("v2", "p3", fee_rate=0.001, slippage_rate=0.002)
    first = HistoricalBacktester().run(candles(), "synthetic", config)
    second = HistoricalBacktester().run(candles(), "synthetic", config)
    assert first == second
    assert first.strategy_version == "v2"
    assert first.parameter_version == "p3"
    assert first.fee_rate == 0.001
    assert first.slippage_rate == 0.002


def test_validated_spot_trade_reaches_backtest_through_production_service() -> None:
    source = complete_input()
    source.data["market"] = "crypto"
    history = [Candle.model_validate(item) for item in source.data["candles"]]
    history.append(
        Candle(
            timestamp=history[-1].timestamp + timedelta(hours=1),
            open=14,
            high=16,
            low=13,
            close=15,
            volume=150,
        )
    )
    frames = {
        name: MarketData.model_validate(data)
        for name, data in timeframe_fixtures(source.data).items()
    }
    result = HistoricalBacktester().run_pipeline(
        history,
        "synthetic-explicit-frames",
        BacktestConfig("v1", "p1"),
        timeframes=frames,
        instrument="TEST",
    )
    assert result.trades == 1
    assert result.trades_detail[0].decision == DecisionState.BUY
    assert (
        result.trades_detail[0].analysis_timestamp == history[-2].timestamp.isoformat()
    )
    assert result.trades_detail[0].exit_timestamp == history[-1].timestamp.isoformat()
    assert result.total_return == pytest.approx(1 / 14)
