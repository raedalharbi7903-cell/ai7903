from dataclasses import dataclass

from app.analysis.models import AnalysisInput, Candle, DecisionState, ValidationStatus
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
    analysis_version: str = "analysis-pipeline-v1"
    validated_decisions: int = 0


class HistoricalBacktester:
    """Sequential evaluator: a decision at index i can only use candles before i."""

    def run(
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
    ) -> BacktestResult:
        """Compatibility entry point; all backtests use the production pipeline."""
        return self.run_pipeline(candles, dataset_id, config)

    def run_pipeline(
        self, candles: list[Candle], dataset_id: str, config: BacktestConfig
    ) -> BacktestResult:
        """Evaluate AnalysisService sequentially without exposing future candles."""
        decisions: list[DecisionState] = []
        returns: list[float] = []
        validated_decisions = 0
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
            if result.validation != ValidationStatus.PASS:
                continue
            validated_decisions += 1
            entry, following = visible[-1].close, candles[index + 1].close
            if result.decision == DecisionState.BUY:
                returns.append(
                    (following - entry) / entry - config.fee_rate - config.slippage_rate
                )
            elif result.decision == DecisionState.SELL:
                returns.append(
                    (entry - following) / entry - config.fee_rate - config.slippage_rate
                )
        return BacktestResult(
            dataset_id,
            tuple(decisions),
            sum(returns),
            len(returns),
            validated_decisions=validated_decisions,
        )


def split_development_oos(
    candles: list[Candle], development_size: int
) -> tuple[list[Candle], list[Candle]]:
    if development_size <= 1 or development_size >= len(candles):
        raise ValueError("Development split must leave out-of-sample data")
    return candles[:development_size], candles[development_size:]
