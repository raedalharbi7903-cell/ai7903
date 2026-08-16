from datetime import UTC, datetime
from uuid import uuid4

from app.analysis.context import AnalysisContext
from app.analysis.models import (
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    Evidence,
    MarketData,
    ValidationStatus,
)


class BaseEngine:
    name = "base"
    family = "system"

    def execute(self, context: AnalysisContext) -> EngineOutput:
        return self.analyze(context)

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name, status=EngineLifecycleStatus.COMPLETED
        )

    def finding(
        self, context: AnalysisContext, text: str, bias: str | None = None
    ) -> Evidence:
        data = context.market_data
        if data is None:
            raise ValueError("Market data is required before evidence generation")
        return Evidence(
            evidence_id=str(uuid4()),
            source_engine=self.name,
            family=self.family,
            instrument=data.instrument,
            market=data.market,
            timeframe=data.timeframe,
            timestamp=datetime.now(UTC),
            finding=text,
            bias=bias,
            provenance={"provider": data.provider, "fixture": str(data.fixture)},
            independent=self.family not in {item.family for item in context.evidence},
        )


class DataEngine(BaseEngine):
    name, family = "data", "data"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        try:
            data = MarketData.model_validate(context.analysis_input.data)
        except Exception as error:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                warnings=[str(error)],
            )
        context.market_data = data
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"fixture": data.fixture, "candles": len(data.candles)},
        )


class MarketContextEngine(BaseEngine):
    name, family = "market_context", "context"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        if context.market_data is None:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                warnings=["missing data"],
            )
        closes = [c.close for c in context.market_data.candles]
        bias = (
            "bullish"
            if closes[-1] > closes[0]
            else "bearish" if closes[-1] < closes[0] else "neutral"
        )
        context.state["context"] = bias
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            evidence=[self.finding(context, f"context is {bias}", bias)],
        )


class PriceFindingEngine(BaseEngine):
    def analyze(self, context: AnalysisContext) -> EngineOutput:
        if context.market_data is None or len(context.market_data.candles) < 2:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=["insufficient candles"],
            )
        closes = [c.close for c in context.market_data.candles]
        bias = (
            "bullish"
            if closes[-1] > closes[0]
            else "bearish" if closes[-1] < closes[0] else "neutral"
        )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            evidence=[self.finding(context, f"{self.name} finding: {bias}", bias)],
        )


class MarketStructureEngine(PriceFindingEngine):
    name, family = "market_structure", "structure"


class TrendEngine(PriceFindingEngine):
    name, family = "trend", "trend"


class SupportResistanceEngine(PriceFindingEngine):
    name, family = "support_resistance", "levels"


class SupplyDemandEngine(PriceFindingEngine):
    name, family = "supply_demand", "zones"


class LiquidityEngine(PriceFindingEngine):
    name, family = "liquidity", "liquidity"


class VolumeEngine(PriceFindingEngine):
    name, family = "volume", "volume"


class MomentumEngine(PriceFindingEngine):
    name, family = "momentum", "momentum"


class VolatilityEngine(PriceFindingEngine):
    name, family = "volatility", "volatility"


class PatternRecognitionEngine(PriceFindingEngine):
    name, family = "pattern_recognition", "pattern"


class CandlestickEngine(PriceFindingEngine):
    name, family = "candlestick", "candlestick"


class CorrelationEngine(PriceFindingEngine):
    name, family = "correlation", "correlation"


class MultiTimeframeEngine(BaseEngine):
    name, family = "multi_timeframe", "timeframe"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"alignment": "single_timeframe"},
            warnings=["multi-timeframe input not supplied"],
        )


class EvidenceEngine(BaseEngine):
    name, family = "evidence", "evidence"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        families = {item.family for item in context.evidence}
        context.state["families"] = families
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"independent_families": len(families)},
        )


class ConfluenceEngine(BaseEngine):
    name, family = "confluence", "confluence"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        directional = [
            item.bias
            for item in context.evidence
            if item.independent and item.bias in {"bullish", "bearish"}
        ]
        aligned = len(set(directional)) == 1 and bool(directional)
        context.state["confluence"] = aligned
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "aligned": aligned,
                "families": len(set(item.family for item in context.evidence)),
            },
        )


class OpportunityFilter(BaseEngine):
    name, family = "opportunity_filter", "filter"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        eligible = (
            bool(context.state.get("confluence")) and context.market_data is not None
        )
        context.state["eligible"] = eligible
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"eligible": eligible},
        )


class DecisionEngine(BaseEngine):
    name, family = "decision", "decision"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        if not context.state.get("eligible"):
            decision = (
                DecisionState.NO_TRADE
                if context.market_data
                else DecisionState.INSUFFICIENT_DATA
            )
        else:
            bias = next(
                (
                    item.bias
                    for item in context.evidence
                    if item.independent and item.bias in {"bullish", "bearish"}
                ),
                None,
            )
            decision = (
                DecisionState.BUY
                if bias == "bullish"
                else DecisionState.SELL if bias == "bearish" else DecisionState.WAIT
            )
        context.state["decision"] = decision
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"decision": decision},
        )


class RiskEngine(BaseEngine):
    name, family = "risk", "risk"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"risk": "calibration_required"},
            warnings=["No empirical risk formula configured"],
        )


class ConfidenceEngine(BaseEngine):
    name, family = "confidence", "confidence"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"confidence": "uncalibrated"},
            warnings=["Confidence is not probability of profit"],
        )


class ValidationEngine(BaseEngine):
    name, family = "validation", "validation"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        status = (
            ValidationStatus.PASS
            if context.market_data and context.state.get("decision")
            else ValidationStatus.FAIL
        )
        context.state["validation"] = status
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"validation": status},
        )


class ExplainabilityEngine(BaseEngine):
    name, family = "explainability", "explainability"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "summary": f"Decision: {context.state.get('decision', 'unavailable')}"
            },
        )


class AIReasoningLayer(BaseEngine):
    name, family = "ai_reasoning", "ai"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.DEGRADED,
            data={"available": False},
            warnings=["AI provider is not configured; deterministic analysis retained"],
        )


class StrategyBacktestingSystem(BaseEngine):
    name, family = "strategy_backtesting", "evaluation"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.DEGRADED,
            data={"mode": "offline_only"},
            warnings=["Historical evaluation data not configured"],
        )


def default_engines() -> tuple[BaseEngine, ...]:
    return (
        DataEngine(),
        MarketContextEngine(),
        MarketStructureEngine(),
        TrendEngine(),
        SupportResistanceEngine(),
        SupplyDemandEngine(),
        LiquidityEngine(),
        VolumeEngine(),
        MomentumEngine(),
        VolatilityEngine(),
        PatternRecognitionEngine(),
        CandlestickEngine(),
        CorrelationEngine(),
        MultiTimeframeEngine(),
        EvidenceEngine(),
        ConfluenceEngine(),
        OpportunityFilter(),
        DecisionEngine(),
        RiskEngine(),
        ConfidenceEngine(),
        ValidationEngine(),
        ExplainabilityEngine(),
        AIReasoningLayer(),
        StrategyBacktestingSystem(),
    )
