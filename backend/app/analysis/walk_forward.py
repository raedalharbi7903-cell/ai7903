"""Chronological fixed-parameter research folds over the existing backtester.

No fitting, parameter optimization, empirical calibration or portfolio simulator.
Training ranges are historical warmup/provenance, not a claim a model was trained.
The configurable gap separates train/test membership; it is not label-horizon
statistical purging. Gap candles remain legitimate past observations at decision
time. Every test window reserves its final candle solely for trade outcomes.
"""

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal

from app.analysis.backtesting import (
    BacktestConfig,
    BacktestResult,
    HistoricalBacktester,
)
from app.analysis.models import Candle, MarketData, ValidationStatus
from app.analysis.providers import validate_market_data
from app.analysis.telemetry import TelemetrySink


@dataclass(frozen=True)
class WalkForwardConfig:
    version: str
    training_size: int
    test_size: int
    window: Literal["expanding", "rolling"]
    gap_size: int = 0
    include_partial: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("Walk-forward configuration version is required")
        for name, minimum in (
            ("training_size", 3),
            ("test_size", 2),
            ("gap_size", 0),
        ):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"Invalid walk-forward {name}")
        if not isinstance(self.window, str) or self.window not in {
            "expanding",
            "rolling",
        }:
            raise ValueError("Window must be expanding or rolling")
        if type(self.include_partial) is not bool:
            raise ValueError("Partial-fold policy must be an explicit boolean")


@dataclass(frozen=True)
class HistoricalFold:
    """Half-open positional ranges; test_end-1 is outcome-only, never a decision."""

    index: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    partial: bool


@dataclass(frozen=True)
class FoldEvaluation:
    fold: HistoricalFold
    train_first_timestamp: str
    train_last_timestamp: str
    first_decision_timestamp: str
    last_decision_timestamp: str
    last_outcome_timestamp: str
    primary_prefix_sha256: str
    auxiliary_prefix_sha256: str
    result: BacktestResult


@dataclass(frozen=True)
class WalkForwardResult:
    dataset_id: str
    content_version: str
    config: WalkForwardConfig
    folds: tuple[FoldEvaluation, ...]
    methodology_version: str = "fixed-parameter-walk-forward-v1"
    training_performed: bool = False
    calibration_status: str = "uncalibrated"
    return_aggregation: str = "per_fold_sum_of_one_bar_spot_long_returns"


def build_folds(length: int, config: WalkForwardConfig) -> tuple[HistoricalFold, ...]:
    """Deterministic nonoverlapping test membership, without reading future values."""
    if type(length) is not int or length < 0:
        raise ValueError("Dataset length must be a nonnegative integer")
    if not isinstance(config, WalkForwardConfig):
        raise ValueError("Explicit walk-forward configuration is required")
    config = replace(config)
    folds = []
    train_end = config.training_size
    while train_end + config.gap_size + 2 <= length:
        start = train_end + config.gap_size
        end = min(start + config.test_size, length)
        partial = end - start < config.test_size
        if partial and not config.include_partial:
            break
        folds.append(
            HistoricalFold(
                index=len(folds),
                train_start=(
                    0
                    if config.window == "expanding"
                    else train_end - config.training_size
                ),
                train_end=train_end,
                test_start=start,
                test_end=end,
                partial=partial,
            )
        )
        train_end += config.test_size
    if not folds:
        raise ValueError("Insufficient history for a complete decision/outcome fold")
    return tuple(folds)


def _fingerprint(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _candles(candles: list[Candle]) -> list[Candle]:
    if (
        not isinstance(candles, list)
        or not candles
        or any(not isinstance(item, Candle) for item in candles)
    ):
        raise ValueError("Explicit historical candles are required")
    # Revalidate copied models and detach them from caller-owned mutable objects.
    snapshot = [
        Candle.model_validate(item.model_dump(warnings="error")) for item in candles
    ]
    primary = MarketData(
        instrument="historical-fixture",
        market="crypto",
        timeframe="1h",
        provider="historical_fixture",
        source_timestamp=snapshot[-1].timestamp,
        candles=snapshot,
        fixture=True,
    )
    if validate_market_data(primary) != ValidationStatus.PASS or any(
        not candle.complete for candle in snapshot
    ):
        raise ValueError(
            "Walk-forward candles must be valid, ordered, aware and closed"
        )
    return snapshot


def _frame_prefixes(
    timeframes: dict[str, MarketData], last_outcome: datetime
) -> dict[str, MarketData]:
    frames = {}
    for role, original in timeframes.items():
        frame = MarketData.model_validate(original.model_dump(warnings="error"))
        if not frame.fixture or validate_market_data(frame) != ValidationStatus.PASS:
            raise ValueError("Walk-forward auxiliary frames must be validated fixtures")
        visible = [c for c in frame.candles if c.timestamp <= last_outcome]
        if visible:
            frames[role] = frame.model_copy(
                update={"candles": visible, "source_timestamp": visible[-1].timestamp}
            )
    return frames


class WalkForwardEvaluator:
    def __init__(self, telemetry: TelemetrySink | None = None) -> None:
        self._backtester = HistoricalBacktester(telemetry)

    def run(
        self,
        candles: list[Candle],
        dataset_id: str,
        content_version: str,
        config: WalkForwardConfig,
        execution: BacktestConfig,
        *,
        timeframes: dict[str, MarketData] | None = None,
        instrument: str = "historical-fixture",
        timeframe: str = "1h",
    ) -> WalkForwardResult:
        if not isinstance(config, WalkForwardConfig):
            raise ValueError("Explicit walk-forward configuration is required")
        config = replace(config)
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (dataset_id, content_version, instrument, timeframe)
        ):
            raise ValueError("Dataset/version/instrument/timeframe must be explicit")
        if any(
            isinstance(value, bool)
            for value in (execution.fee_rate, execution.slippage_rate)
        ):
            raise ValueError("Execution costs must not be booleans")
        execution = replace(execution)
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (execution.strategy_version, execution.parameter_version)
        ):
            raise ValueError(
                "Execution strategy and parameter versions must be explicit"
            )
        snapshot = _candles(candles)
        evaluations = []
        for fold in build_folds(len(snapshot), config):
            visible = snapshot[fold.train_start : fold.test_end]
            frames = _frame_prefixes(timeframes or {}, visible[-1].timestamp)
            evaluated = self._backtester.run_pipeline(
                visible,
                f"{dataset_id}:fold:{fold.index}",
                execution,
                timeframes=frames,
                instrument=instrument,
                timeframe=timeframe,
                decision_start_index=fold.test_start - fold.train_start,
                decision_end_index=fold.test_end - fold.train_start - 1,
            )
            evaluations.append(
                FoldEvaluation(
                    fold=fold,
                    train_first_timestamp=snapshot[
                        fold.train_start
                    ].timestamp.isoformat(),
                    train_last_timestamp=snapshot[
                        fold.train_end - 1
                    ].timestamp.isoformat(),
                    first_decision_timestamp=snapshot[
                        fold.test_start
                    ].timestamp.isoformat(),
                    last_decision_timestamp=snapshot[
                        fold.test_end - 2
                    ].timestamp.isoformat(),
                    last_outcome_timestamp=snapshot[
                        fold.test_end - 1
                    ].timestamp.isoformat(),
                    primary_prefix_sha256=_fingerprint(
                        [item.model_dump(mode="json") for item in visible]
                    ),
                    auxiliary_prefix_sha256=_fingerprint(
                        {
                            name: data.model_dump(mode="json")
                            for name, data in frames.items()
                        }
                    ),
                    result=evaluated,
                )
            )
        return WalkForwardResult(
            dataset_id, content_version, config, tuple(evaluations)
        )
