from dataclasses import dataclass

from app.analysis.models import Candle, DecisionState
from app.analysis.models import AnalysisInput
from app.analysis.service import AnalysisService


@dataclass(frozen=True)
class BacktestConfig:
    strategy_version: str
    parameter_version: str
    fee_rate: float = 0.0
    slippage_rate: float = 0.0


@dataclass(frozen=True)
class BacktestResult:
    dataset_id: str
    decisions: tuple[DecisionState, ...]
    total_return: float
    trades: int


class HistoricalBacktester:
    """Sequential evaluator: a decision at index i can only use candles before i."""

    def run(
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
    ) -> BacktestResult:
        if len(candles) < 3:
            raise ValueError("At least three candles are required")
        decisions: list[DecisionState] = []
        returns: list[float] = []
        for index in range(1, len(candles) - 1):
            previous, current, future = (
                candles[index - 1],
                candles[index],
                candles[index + 1],
            )
            decision = (
                DecisionState.BUY
                if current.close > previous.close
                else (
                    DecisionState.SELL
                    if current.close < previous.close
                    else DecisionState.NO_TRADE
                )
            )
            decisions.append(decision)
            if decision == DecisionState.BUY:
                returns.append(
                    (future.close - current.close) / current.close
                    - config.fee_rate
                    - config.slippage_rate
                )
            elif decision == DecisionState.SELL:
                returns.append(
                    (current.close - future.close) / current.close
                    - config.fee_rate
                    - config.slippage_rate
                )
        return BacktestResult(dataset_id, tuple(decisions), sum(returns), len(returns))

    def run_pipeline(
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
    ) -> BacktestResult:
        """Evaluate the production AnalysisService sequentially with no future candles."""
        decisions: list[DecisionState] = []
        returns: list[float] = []
        service = AnalysisService()
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
                    }
                )
            )
            decisions.append(result.decision)
            if result.validation.value != "pass":
                continue
            entry, following = visible[-1].close, candles[index + 1].close
            if result.decision == DecisionState.BUY:
                returns.append(
                    (following - entry) / entry - config.fee_rate - config.slippage_rate
                )
            elif result.decision == DecisionState.SELL:
                returns.append(
                    (entry - following) / entry - config.fee_rate - config.slippage_rate
                )
        return BacktestResult(dataset_id, tuple(decisions), sum(returns), len(returns))


def split_development_oos(
    candles: list[Candle], development_size: int
) -> tuple[list[Candle], list[Candle]]:
    if development_size <= 1 or development_size >= len(candles):
        raise ValueError("Development split must leave out-of-sample data")
    return candles[:development_size], candles[development_size:]
