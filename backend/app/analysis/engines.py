from datetime import UTC, datetime
from uuid import uuid4

from app.analysis.context import AnalysisContext
from app.analysis.deterministic import analyze, correlation
from app.analysis.freshness import FreshnessPolicy, assess_candles, assess_market_data
from app.analysis.models import (
    Candle,
    DecisionState,
    EngineLifecycleStatus,
    EngineOutput,
    Evidence,
    FreshnessStatus,
    MarketData,
    ValidationStatus,
)
from app.analysis.providers import validate_market_data


def _freshness_policy(context: AnalysisContext) -> FreshnessPolicy:
    configured = context.analysis_input.metadata.get("freshness_policy", {})
    return FreshnessPolicy(
        delayed_after_intervals=int(configured.get("delayed_after_intervals", 1)),
        stale_after_intervals=int(configured.get("stale_after_intervals", 3)),
        timeframe_seconds=configured.get("timeframe_seconds"),
    )


def _decision_timestamp(context: AnalysisContext, data: MarketData) -> datetime:
    raw = context.analysis_input.metadata.get("decision_timestamp")
    if isinstance(raw, str):
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if isinstance(raw, datetime):
        return raw
    return data.candles[-1].timestamp if data.fixture else data.source_timestamp


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
        quality = validate_market_data(data)
        data.quality_status = quality
        reference = _decision_timestamp(context, data)
        freshness = assess_market_data(data, reference, _freshness_policy(context))
        data.freshness_status = freshness.status
        data.freshness_reason = freshness.reason
        if quality == ValidationStatus.FAIL:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                warnings=["market data quality validation failed"],
            )
        if freshness.status in {FreshnessStatus.STALE, FreshnessStatus.INVALID}:
            data.quality_status = ValidationStatus.DEGRADED
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                data={"freshness": freshness.status, "reason": freshness.reason},
                warnings=[f"market data freshness is {freshness.status}"],
            )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "fixture": data.fixture,
                "candles": len(data.candles),
                "quality": quality,
                "freshness": freshness.status,
                "freshness_reason": freshness.reason,
            },
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
        observation, bias, measurements = analyze(
            self.name, context.market_data.candles
        )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data=measurements,
            evidence=[self.finding(context, observation, bias)],
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


class MomentumDivergenceEngine(PriceFindingEngine):
    name, family = "momentum_divergence", "momentum"


class LiquiditySweepEngine(PriceFindingEngine):
    name, family = "liquidity_sweep", "liquidity"


class MarketTransitionEngine(PriceFindingEngine):
    name, family = "market_transition", "structure"


class VolumeAnomalyEngine(PriceFindingEngine):
    name, family = "volume_anomaly", "volume"


class CorrelationEngine(PriceFindingEngine):
    name, family = "correlation", "correlation"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        benchmark = context.analysis_input.metadata.get("benchmark_candles")
        data = context.market_data
        if data is None or not benchmark:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=["benchmark data unavailable"],
            )
        try:
            benchmark_candles = [Candle.model_validate(item) for item in benchmark]
        except (TypeError, ValueError) as error:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=[f"invalid benchmark data: {error}"],
            )
        decision_time = data.candles[-1].timestamp
        benchmark_freshness = assess_candles(
            benchmark_candles,
            data.timeframe,
            decision_time,
            _freshness_policy(context),
        )
        if benchmark_freshness.status in {
            FreshnessStatus.STALE,
            FreshnessStatus.INVALID,
        }:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                data={
                    "freshness": benchmark_freshness.status,
                    "reason": benchmark_freshness.reason,
                },
                warnings=["benchmark freshness prevents contextual correlation"],
            )
        benchmark_by_time = {
            candle.timestamp: candle
            for candle in benchmark_candles
            if candle.timestamp <= decision_time
        }
        aligned = [
            (candle.close, benchmark_by_time[candle.timestamp].close)
            for candle in data.candles
            if candle.timestamp in benchmark_by_time
        ]
        value = correlation(
            [item[0] for item in aligned], [item[1] for item in aligned]
        )
        if value is None:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=["insufficient aligned history"],
            )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "coefficient": value,
                "sample_size": len(aligned),
                "methodology": "Pearson correlation on timestamp-aligned closes",
                "benchmark_provider": context.analysis_input.metadata.get(
                    "benchmark_provider", "unspecified"
                ),
                "freshness": benchmark_freshness.status,
            },
            evidence=[
                self.finding(
                    context,
                    "benchmark correlation is contextual and not a directional vote",
                )
            ],
        )


class MultiTimeframeEngine(BaseEngine):
    name, family = "multi_timeframe", "timeframe"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        raw_frames = context.analysis_input.metadata.get("timeframes", {})
        required = ("htf", "itf", "ltf")
        if not all(name in raw_frames for name in required):
            context.state["mtf_alignment"] = "unavailable"
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                data={"alignment": "unavailable", "required": required},
                warnings=["HTF, ITF, and LTF inputs are required for MTF analysis"],
            )
        if context.market_data is None:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                warnings=["primary market data unavailable"],
            )
        summaries: dict[str, dict[str, object]] = {}
        decision_time = context.market_data.candles[-1].timestamp
        for name in required:
            try:
                frame = MarketData.model_validate(raw_frames[name])
            except (TypeError, ValueError) as error:
                context.state["mtf_alignment"] = "unavailable"
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.DEGRADED,
                    warnings=[f"invalid {name} input: {error}"],
                )
            quality = validate_market_data(frame)
            if quality != ValidationStatus.PASS:
                context.state["mtf_alignment"] = "degraded"
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.DEGRADED,
                    warnings=[f"{name} data quality is {quality}"],
                )
            freshness = assess_market_data(
                frame, decision_time, _freshness_policy(context)
            )
            frame.freshness_status = freshness.status
            frame.freshness_reason = freshness.reason
            if freshness.status in {FreshnessStatus.STALE, FreshnessStatus.INVALID}:
                context.state["mtf_alignment"] = "degraded"
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.DEGRADED,
                    data={"freshness": freshness.status, "reason": freshness.reason},
                    warnings=[f"{name} freshness is {freshness.status}"],
                )
            if len(frame.candles) < 5:
                context.state["mtf_alignment"] = "degraded"
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.DEGRADED,
                    warnings=[f"{name} has insufficient completed candle history"],
                )
            observation, bias, measurements = analyze("trend", frame.candles)
            summaries[name] = {
                "bias": bias,
                "observation": observation,
                "measurements": measurements,
                "source_timestamp": frame.source_timestamp.isoformat(),
                "completed_candle_timestamp": frame.candles[-1].timestamp.isoformat(),
                "provider": frame.provider,
                "quality": quality,
                "freshness": freshness.status,
            }
        directions = [str(summaries[name]["bias"]) for name in required]
        alignment = "aligned" if len(set(directions)) == 1 else "conflict"
        context.state["mtf_alignment"] = alignment
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"alignment": alignment, "timeframes": summaries},
            evidence=[
                self.finding(
                    context,
                    f"MTF {alignment}: " + ", ".join(directions),
                    directions[0] if alignment == "aligned" else None,
                )
            ],
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
        family_biases: dict[str, set[str]] = {}
        for item in context.evidence:
            if item.independent and item.bias in {"bullish", "bearish"}:
                family_biases.setdefault(item.family, set()).add(item.bias)
        conflicted_families = {
            family for family, biases in family_biases.items() if len(biases) > 1
        }
        directional = [
            next(iter(biases))
            for family, biases in family_biases.items()
            if family not in conflicted_families
        ]
        aligned = len(set(directional)) == 1 and bool(directional)
        context.state["confluence"] = aligned
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "aligned": aligned,
                "families": len(family_biases),
                "conflicted_families": sorted(conflicted_families),
            },
        )


class OpportunityFilter(BaseEngine):
    name, family = "opportunity_filter", "filter"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        eligible = (
            bool(context.state.get("confluence")) and context.market_data is not None
        )
        if context.state.get("mtf_alignment") == "conflict":
            eligible = False
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
        elif (
            context.market_data
            and context.market_data.freshness_status == FreshnessStatus.DELAYED
        ):
            decision = DecisionState.WAIT
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
        data = context.market_data
        structure = context.output("market_structure")
        decision = context.state.get("decision")
        if decision not in {DecisionState.BUY, DecisionState.SELL}:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=[
                    "structural risk applies only to executable directional decisions"
                ],
            )
        if data is None or structure is None:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=["risk inputs unavailable"],
            )
        price = data.candles[-1].close
        invalidation = structure.data.get("invalidation")
        if not isinstance(invalidation, int | float) or invalidation == price:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.DEGRADED,
                warnings=["structural invalidation unavailable"],
            )
        is_buy = decision == DecisionState.BUY
        valid_stop = invalidation < price if is_buy else invalidation > price
        if not valid_stop:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                warnings=["structural invalidation is directionally invalid"],
            )
        risk = abs(price - invalidation)
        volatility = context.output("volatility")
        liquidity = context.output("liquidity")
        relative_atr = (
            volatility.data.get("relative_atr")
            if volatility and volatility.status == EngineLifecycleStatus.COMPLETED
            else None
        )
        atr = volatility.data.get("atr") if volatility else None
        min_atr_multiple = float(
            context.analysis_input.metadata.get("minimum_stop_atr_multiple", 0.5)
        )
        max_atr_multiple = float(
            context.analysis_input.metadata.get("maximum_stop_atr_multiple", 5.0)
        )
        if isinstance(atr, int | float) and atr > 0:
            if risk < atr * min_atr_multiple:
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.FAILED,
                    warnings=["structural stop is too tight for observed volatility"],
                )
            if risk > atr * max_atr_multiple:
                return EngineOutput(
                    engine_name=self.name,
                    status=EngineLifecycleStatus.FAILED,
                    warnings=["structural stop is too wide for observed volatility"],
                )
        levels = context.output("support_resistance")
        structural_target = None
        if levels:
            structural_target = (
                levels.data.get("resistance") if is_buy else levels.data.get("support")
            )
        minimum_rr = float(
            context.analysis_input.metadata.get("minimum_risk_reward", 1.0)
        )
        projected_target = price + risk * 2 if is_buy else price - risk * 2
        structural_candidate = (
            min(projected_target, structural_target)
            if is_buy
            and isinstance(structural_target, int | float)
            and structural_target > price
            else (
                max(projected_target, structural_target)
                if not is_buy
                and isinstance(structural_target, int | float)
                and structural_target < price
                else projected_target
            )
        )
        candidate_rr = abs(structural_candidate - price) / risk
        target = (
            structural_candidate if candidate_rr >= minimum_rr else projected_target
        )
        risk_reward = abs(target - price) / risk
        if risk_reward < minimum_rr:
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.FAILED,
                data={"risk_reward": risk_reward, "minimum_risk_reward": minimum_rr},
                warnings=["risk/reward is below configured minimum"],
            )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "invalidation": invalidation,
                "stop_loss": invalidation,
                "target": target,
                "risk_reward": risk_reward,
                "structural_risk": risk,
                "risk_quality": (
                    "structural_volatility_aware"
                    if isinstance(atr, int | float) and atr > 0
                    else "structural_without_volatility"
                ),
                "relative_atr": relative_atr,
                "liquidity_context": (
                    "ohlcv_inference"
                    if liquidity and liquidity.status == EngineLifecycleStatus.COMPLETED
                    else "unavailable"
                ),
            },
        )


class ConfidenceEngine(BaseEngine):
    name, family = "confidence", "confidence"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        families = len({item.family for item in context.evidence if item.independent})
        alignment = context.state.get("mtf_alignment", "unknown")
        risk = context.output("risk")
        data_quality = (
            context.market_data.quality_status
            if context.market_data
            else ValidationStatus.FAIL
        )
        penalties: list[str] = []
        if data_quality != ValidationStatus.PASS:
            penalties.append("data_quality")
        if (
            context.market_data
            and context.market_data.freshness_status != FreshnessStatus.FRESH
        ):
            penalties.append("freshness")
        if alignment in {"conflict", "degraded", "unavailable"}:
            penalties.append("multi_timeframe")
        if risk is None or risk.status != EngineLifecycleStatus.COMPLETED:
            penalties.append("risk_quality")
        label = (
            "high"
            if context.state.get("confluence") and families >= 3 and not penalties
            else (
                "medium"
                if context.state.get("confluence") and families >= 2 and not penalties
                else "low"
            )
        )
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={
                "confidence": label,
                "calibration": "uncalibrated",
                "independent_families": families,
                "mtf_alignment": alignment,
                "data_quality": data_quality,
                "penalties": penalties,
                "methodology_version": "analytical-quality-v1",
            },
            warnings=["Confidence is analytical quality, not probability of profit"],
        )


class ValidationEngine(BaseEngine):
    name, family = "validation", "validation"

    def analyze(self, context: AnalysisContext) -> EngineOutput:
        decision = context.state.get("decision")
        risk = context.output("risk")
        confidence = context.output("confidence")
        reasons: list[str] = []
        status = ValidationStatus.PASS
        if context.market_data is None or decision is None:
            status = ValidationStatus.FAIL
            reasons.append("market data or decision unavailable")
        elif decision in {DecisionState.BUY, DecisionState.SELL}:
            if risk is None or risk.status != EngineLifecycleStatus.COMPLETED:
                status = ValidationStatus.FAIL
                reasons.append("executable decision lacks valid structural risk")
            if context.state.get("mtf_alignment") in {
                "conflict",
                "degraded",
                "unavailable",
            }:
                status = ValidationStatus.FAIL
                reasons.append(
                    "multi-timeframe confirmation unavailable or conflicting"
                )
            if context.market_data.freshness_status not in {
                FreshnessStatus.FRESH,
                FreshnessStatus.DELAYED,
            }:
                status = ValidationStatus.FAIL
                reasons.append("primary market data freshness is unacceptable")
        if confidence is None:
            status = ValidationStatus.FAIL
            reasons.append("confidence output unavailable")
        context.state["validation"] = status
        return EngineOutput(
            engine_name=self.name,
            status=EngineLifecycleStatus.COMPLETED,
            data={"validation": status, "reasons": reasons},
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
        MomentumDivergenceEngine(),
        VolatilityEngine(),
        VolumeAnomalyEngine(),
        PatternRecognitionEngine(),
        CandlestickEngine(),
        LiquiditySweepEngine(),
        MarketTransitionEngine(),
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
