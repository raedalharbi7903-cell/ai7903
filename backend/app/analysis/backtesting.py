from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from app.analysis.models import AnalysisInput, Candle, DecisionState, ValidationStatus
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
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
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
            for index in range(2, len(candles) - 1):
                visible = candles[: index + 1]
                result = service.analyze(
                    AnalysisInput(
                        data={
                            "instrument": "historical-fixture",
                            "market": "crypto",
                            "timeframe": "fixture",
                            "provider": "historical_fixture",
                            "source_timestamp": visible[-1].timestamp,
                            "candles": [item.model_dump() for item in visible],
                            "fixture": True,
                        },
                        metadata={
                            "timeframes": {
                                name: {
                                    "instrument": "historical-fixture",
                                    "market": "crypto",
                                    "timeframe": "fixture",
                                    "provider": "historical_fixture",
                                    "source_timestamp": visible[-1].timestamp,
                                    "candles": [item.model_dump() for item in visible],
                                    "fixture": True,
                                }
                                for name in ("htf", "itf", "ltf")
                            }
                        },
                    )
                )
                decisions.append(result.decision)
                if result.validation != ValidationStatus.PASS:
                    continue
                validated_decisions += 1
                if result.decision not in {DecisionState.BUY, DecisionState.SELL}:
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
                trade = _execute_trade(
                    result.decision,
                    visible[-1],
                    candles[index + 1],
                    float(risk.data["stop_loss"]),
                    float(risk.data["target"]),
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
    is_buy = decision == DecisionState.BUY
    entry = decision_candle.close * (
        1 + config.slippage_rate if is_buy else 1 - config.slippage_rate
    )
    hit_stop = execution_candle.low <= stop if is_buy else execution_candle.high >= stop
    hit_target = (
        execution_candle.high >= target if is_buy else execution_candle.low <= target
    )
    if hit_stop:
        # Deliberately conservative when both stop and target are crossed.
        exit_price, exit_reason = stop, "stop"
    elif hit_target:
        exit_price, exit_reason = target, "target"
    else:
        exit_price, exit_reason = execution_candle.close, "next_candle_close"
    gross = (exit_price - entry) / entry if is_buy else (entry - exit_price) / entry
    return BacktestTrade(
        decision=decision,
        entry_timestamp=decision_candle.timestamp.isoformat(),
        exit_timestamp=execution_candle.timestamp.isoformat(),
        entry_price=entry,
        exit_price=exit_price,
        exit_reason=exit_reason,
        return_after_costs=gross - 2 * config.fee_rate,
        analysis_timestamp=decision_candle.timestamp.isoformat(),
    )


def split_development_oos(
    candles: list[Candle], development_size: int
) -> tuple[list[Candle], list[Candle]]:
    if development_size <= 1 or development_size >= len(candles):
        raise ValueError("Development split must leave out-of-sample data")
    return candles[:development_size], candles[development_size:]
