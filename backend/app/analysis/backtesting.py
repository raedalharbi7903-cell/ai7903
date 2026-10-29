from dataclasses import dataclass
from math import isfinite
from time import perf_counter
from uuid import uuid4

from app.analysis.models import (
    AnalysisInput,
    Candle,
    DecisionState,
    MarketData,
    ValidationStatus,
)
from app.analysis.providers import validate_market_data
from app.analysis.service import AnalysisService
from app.analysis.telemetry import BacktestTelemetry, NullTelemetrySink, TelemetrySink


@dataclass(frozen=True)
class BacktestConfig:
    strategy_version: str
    parameter_version: str
    fee_rate: float = 0.0
    slippage_rate: float = 0.0
    entry_timing: str = "decision_close"
    same_candle_policy: str = "stop_first"

    def __post_init__(self) -> None:
        if not self.strategy_version or not self.parameter_version:
            raise ValueError("Strategy and parameter versions are required")
        for value in (self.fee_rate, self.slippage_rate):
            if not isfinite(value) or not 0 <= value < 1:
                raise ValueError("Execution cost rates must be finite in [0, 1)")
        if (
            self.entry_timing != "decision_close"
            or self.same_candle_policy != "stop_first"
        ):
            raise ValueError("Unsupported execution assumptions")


@dataclass(frozen=True)
class BacktestResult:
    dataset_id: str
    decisions: tuple[DecisionState, ...]
    total_return: float
    trades: int
    analysis_version: str = "analysis-pipeline-v1"
    validated_decisions: int = 0
    trades_detail: tuple["BacktestTrade", ...] = ()
    execution_assumptions: str = (
        "decision_close; stop_first when intrabar ordering is unknown"
    )
    strategy_version: str = ""
    parameter_version: str = ""
    fee_rate: float = 0.0
    slippage_rate: float = 0.0
    return_aggregation: str = "sum_of_one_bar_spot_long_returns"


@dataclass(frozen=True)
class BacktestTrade:
    decision: DecisionState
    entry_timestamp: str
    exit_timestamp: str
    entry_price: float
    exit_price: float
    exit_reason: str
    return_after_costs: float
    analysis_timestamp: str


class HistoricalBacktester:
    """Sequential evaluator: a decision at index i can only use candles before i."""

    def __init__(self, telemetry: TelemetrySink | None = None) -> None:
        self._telemetry = telemetry or NullTelemetrySink()

    def run(
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
    ) -> BacktestResult:
        """Compatibility entry point; all backtests use the production pipeline."""
        return self.run_pipeline(candles, dataset_id, config)

    def run_pipeline(
        self,
        candles: list[Candle],
        dataset_id: str,
        config: BacktestConfig,
        *,
        timeframes: dict[str, MarketData] | None = None,
        instrument: str = "historical-fixture",
        timeframe: str = "1h",
    ) -> BacktestResult:
        """Evaluate AnalysisService sequentially without exposing future candles."""
        backtest_id = str(uuid4())
        started = perf_counter()
        self._record_telemetry(
            BacktestTelemetry(
                event="started",
                backtest_id=backtest_id,
                duration_ms=0.0,
                historical_analysis_count=0,
                validated_decision_count=0,
                rejected_decision_count=0,
                executed_trade_count=0,
                parameter_version=config.parameter_version,
                strategy_version=config.strategy_version,
                analysis_version="analysis-pipeline-v1",
                data_source="historical_fixture",
            )
        )
        decisions: list[DecisionState] = []
        returns: list[float] = []
        trades: list[BacktestTrade] = []
        validated_decisions = 0
        service = AnalysisService(self._telemetry)
        try:
            if len(candles) < 3:
                raise ValueError("At least three candles are required for backtesting")
            primary = MarketData(
                instrument=instrument,
                market="crypto",
                timeframe=timeframe,
                provider="historical_fixture",
                source_timestamp=candles[-1].timestamp,
                candles=candles,
                fixture=True,
            )
            if validate_market_data(primary) != ValidationStatus.PASS or any(
                not candle.complete for candle in candles
            ):
                raise ValueError("Historical candles must be valid, ordered and closed")
            for frame in (timeframes or {}).values():
                if (
                    not frame.fixture
                    or validate_market_data(frame) != ValidationStatus.PASS
                ):
                    raise ValueError("Historical frames must be validated fixtures")
            for index in range(2, len(candles) - 1):
                visible = candles[: index + 1]
                result = service.analyze(
                    AnalysisInput(
                        data={
                            **primary.model_dump(),
                            "source_timestamp": visible[-1].timestamp,
                            "candles": [item.model_dump() for item in visible],
                        },
                        metadata={
                            "decision_timestamp": visible[-1].timestamp,
                            "timeframes": _visible_frames(
                                timeframes or {}, visible[-1]
                            ),
                        },
                    )
                )
                decisions.append(result.decision)
                if result.validation != ValidationStatus.PASS:
                    continue
                validated_decisions += 1
                # Spot-only evaluator: SELL is not an authorization to open a short.
                if result.decision != DecisionState.BUY:
                    continue
                risk = next(
                    (
                        output
                        for output in result.outputs
                        if output.engine_name == "risk"
                    ),
                    None,
                )
                if risk is None or not {"stop_loss", "target"} <= risk.data.keys():
                    continue
                stop = float(risk.data["stop_loss"])
                target = float(risk.data["target"])
                entry = visible[-1].close * (1 + config.slippage_rate)
                if not all(isfinite(value) for value in (entry, stop, target)) or not (
                    0 < stop < entry < target
                ):
                    continue
                trade = _execute_trade(
                    result.decision,
                    visible[-1],
                    candles[index + 1],
                    stop,
                    target,
                    config,
                )
                returns.append(trade.return_after_costs)
                trades.append(trade)
        except Exception as error:
            self._record_telemetry(
                BacktestTelemetry(
                    event="failed",
                    backtest_id=backtest_id,
                    duration_ms=round((perf_counter() - started) * 1000, 3),
                    historical_analysis_count=len(decisions),
                    validated_decision_count=validated_decisions,
                    rejected_decision_count=len(decisions) - validated_decisions,
                    executed_trade_count=len(trades),
                    parameter_version=config.parameter_version,
                    strategy_version=config.strategy_version,
                    analysis_version="analysis-pipeline-v1",
                    data_source="historical_fixture",
                    error_category=type(error).__name__,
                )
            )
            raise
        result = BacktestResult(
            dataset_id,
            tuple(decisions),
            sum(returns),
            len(trades),
            validated_decisions=validated_decisions,
            trades_detail=tuple(trades),
            execution_assumptions=(
                f"{config.entry_timing}; {config.same_candle_policy} when intrabar "
                "ordering is unknown"
            ),
            strategy_version=config.strategy_version,
            parameter_version=config.parameter_version,
            fee_rate=config.fee_rate,
            slippage_rate=config.slippage_rate,
        )
        self._record_telemetry(
            BacktestTelemetry(
                event="completed",
                backtest_id=backtest_id,
                duration_ms=round((perf_counter() - started) * 1000, 3),
                historical_analysis_count=len(decisions),
                validated_decision_count=validated_decisions,
                rejected_decision_count=len(decisions) - validated_decisions,
                executed_trade_count=len(trades),
                parameter_version=config.parameter_version,
                strategy_version=config.strategy_version,
                analysis_version=result.analysis_version,
                data_source="historical_fixture",
            )
        )
        return result

    def _record_telemetry(self, event: BacktestTelemetry) -> None:
        try:
            self._telemetry.record_backtest(event)
        except Exception:
            pass


def _execute_trade(
    decision: DecisionState,
    decision_candle: Candle,
    execution_candle: Candle,
    stop: float,
    target: float,
    config: BacktestConfig,
) -> BacktestTrade:
    if decision != DecisionState.BUY:
        raise ValueError("Spot evaluator does not open short positions")
    if execution_candle.timestamp <= decision_candle.timestamp:
        raise ValueError("Execution must follow the decision candle")
    is_buy = True
    entry = decision_candle.close * (
        1 + config.slippage_rate if is_buy else 1 - config.slippage_rate
    )
    if not all(isfinite(value) for value in (entry, stop, target)) or not (
        0 < stop < entry < target
    ):
        raise ValueError("Invalid execution risk geometry")
    hit_stop = execution_candle.low <= stop
    hit_target = (
        execution_candle.high >= target if is_buy else execution_candle.low <= target
    )
    if hit_stop:
        # Deliberately conservative when both stop and target are crossed.
        exit_price, exit_reason = min(stop, execution_candle.open), "stop"
    elif hit_target:
        exit_price, exit_reason = target, "target"
    else:
        exit_price, exit_reason = execution_candle.close, "next_candle_close"
    exit_price *= 1 - config.slippage_rate
    gross = (exit_price - entry) / entry
    costs = config.fee_rate * (1 + exit_price / entry)
    return BacktestTrade(
        decision=decision,
        entry_timestamp=decision_candle.timestamp.isoformat(),
        exit_timestamp=execution_candle.timestamp.isoformat(),
        entry_price=entry,
        exit_price=exit_price,
        exit_reason=exit_reason,
        return_after_costs=gross - costs,
        analysis_timestamp=decision_candle.timestamp.isoformat(),
    )


def _visible_frames(frames: dict[str, MarketData], decision: Candle) -> dict[str, dict]:
    snapshots = {}
    for role, frame in frames.items():
        visible = []
        for candle in frame.candles:
            if not candle.complete or candle.timestamp > decision.timestamp:
                break
            visible.append(candle)
        if visible:
            snapshots[role] = {
                **frame.model_dump(),
                "candles": [c.model_dump() for c in visible],
                "source_timestamp": visible[-1].timestamp,
            }
    return snapshots


def split_development_oos(
    candles: list[Candle], development_size: int
) -> tuple[list[Candle], list[Candle]]:
    if development_size <= 1 or development_size >= len(candles):
        raise ValueError("Development split must leave out-of-sample data")
    if any(
        b.timestamp <= a.timestamp for a, b in zip(candles, candles[1:], strict=False)
    ):
        raise ValueError("Development/OOS data must be strictly chronological")
    return candles[:development_size], candles[development_size:]
