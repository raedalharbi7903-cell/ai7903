from dataclasses import dataclass

from app.analysis.models import Candle, DecisionState


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


def split_development_oos(
    candles: list[Candle], development_size: int
) -> tuple[list[Candle], list[Candle]]:
    if development_size <= 1 or development_size >= len(candles):
        raise ValueError("Development split must leave out-of-sample data")
    return candles[:development_size], candles[development_size:]
