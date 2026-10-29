---
title: Analysis Pipeline
document_id: DOC-ARCH-PIPELINE-001
version: 2.5.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-16
related_documents: [DOC-ANALYSIS-CATALOG-001, DOC-ANALYSIS-DEPENDENCY_MODEL-001]
---

# Analysis Pipeline

## Purpose

Define lifecycle, provenance, performance, and degraded output policy from market data to user-facing analysis.

## Scope

The generic sequential pipeline/registry, fixture-backed deterministic components, validation gates, MTF input handling, correlation alignment, and sequential historical evaluation are implemented. Live commercial providers, empirical calibration, AI providers, and approved historical datasets remain unavailable.

## Main Content

Lifecycle: acquire attributable data; validate/normalize/snapshot; establish context; run dependency-ordered deterministic engines; align timeframes; create evidence; assess confluence; filter opportunity; form decision; assess risk/confidence; validate; create explainability; optionally invoke AI; return qualified final response.

Provenance must trace Provider → Market → Exchange → Instrument → Timeframe → Timestamp → snapshot/version where applicable → engine → finding → evidence → decision → validation → explanation. Cache/reuse only immutable snapshots or results with provenance and freshness, prevent duplicate analysis, and invoke AI only on validated structured outputs. Observe request-level data, deterministic-compute, infrastructure, and AI costs.

Never fabricate a complete result when a provider is unavailable, data is stale/missing, an engine fails, a timeframe is missing, evidence is insufficient, or validation fails. Explicit status/warnings/errors are mandatory. Only validation-approved DEGRADED output may continue; AI unavailability never authorizes a fabricated narrative.

### Implemented validation integration

The runtime pipeline in `backend/app/analysis/` executes the canonical engines in order. Directional BUY/SELL decisions require completed structural risk and MTF confirmation. An invalid or unavailable risk output, an unavailable/degraded/conflicting MTF result, or missing confidence output causes validation failure and the public result is normalized to `NO_TRADE`. This is a safety gate, not a trading recommendation.

MTF accepts separate `htf`, `itf`, and `ltf` OHLCV inputs. Each is parsed and quality-checked independently, requires at least five completed candles, and is rejected when its latest completed candle is after the primary decision time. The current implementation uses the deterministic trend observation for each frame, then emits aligned/conflict evidence with provider and timestamp provenance.

Correlation aligns benchmark and primary candles by timestamp, excludes benchmark candles after the primary decision time, and reports a Pearson coefficient only with enough overlapping timestamps. Correlation evidence is explicitly contextual and contributes no directional vote.

### Freshness and execution safety

Freshness uses explicit candle-interval policy rather than current wall-clock time. The default policy recognizes documented timeframes and classifies inputs as `fresh`, `delayed`, `stale`, `missing`, or `invalid`. Fixture and historical processing uses the final visible candle as decision-time reference; live input uses source timestamp unless a decision timestamp is explicitly supplied. A stale or invalid primary input prevents a validated directional result. MTF and benchmark inputs are assessed independently against the primary decision time. Incomplete final candles are not treated as finalized observations.

Historical execution invokes the production service with only a visible candle prefix. Entry occurs at the decision close with configured slippage and fees. Stops and targets are evaluated on the next candle; if both are reached in one candle, stop-first is intentionally applied. This is an explicit conservative assumption, not intrabar reconstruction.

### Decision-state semantics and behavioral evidence

The public decision vocabulary is exercised through the production service. `BUY` and `SELL` require eligible aligned evidence and successful risk/validation gates. `NO_TRADE` represents an ineligible opportunity such as MTF conflict. `WAIT` represents otherwise eligible analysis whose primary input is delayed rather than fresh; it preserves a safe request to wait for a completed fresher candle. `INSUFFICIENT_DATA` is returned when no usable market input can be established.

Risk targets are derived internally from structural risk and optional support/resistance context; callers cannot submit arbitrary target overrides. Internal geometry is still validated: invalid structural targets and poor structural reward/risk are rejected, never replaced by a more optimistic projection. ATR minimum/maximum distance controls are configurable metadata policies; they are analytical guards, not position-sizing advice. Nonfinite or malformed volatility observations fail closed. Liquidity remains an OHLCV inference, never observed order-book depth.

Supported deterministic behavior has dedicated regression coverage for structure/trend direction, candle-derived levels/zones, OHLCV liquidity/volume context, momentum/volatility history boundaries, candlestick observations, correlation, MTF safety, decision states and production-pipeline failures. Advanced runtime behavior includes regular/hidden bullish/bearish divergence, confirmed structure breaks, inferred liquidity sweeps, volume anomaly and both engulfing directions, hammer, shooting star and doji. Institutional-order assertions and observed order-book depth remain unsupported. These are deterministic observations, not guaranteed reversals or calibrated profitability claims.

Evidence observation timestamps use the last closed candle; generation time is
separate. Final safety reconciliation also covers engine failures occurring after
the validation engine. Historical evaluation is spot-long-only and does not open
shorts for SELL. Incomplete tails cannot refresh stale closed history. Missing
volume is unavailable, not a vote based on an older retained sample.

### Production reachability matrix

| Component | Implementation / entry | Input → consumer | Failure behavior | Verification | Status |
|---|---|---|---|---|---|
| Data | `engines.py:DataEngine` | input → all engines | failed/degraded quality or freshness | `test_freshness_telemetry.py` | CONNECTED_AND_TESTED |
| Market Context | `MarketContextEngine` | candles → evidence | missing-data failure | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Market Structure | `MarketStructureEngine` | candles → risk | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Trend | `TrendEngine` | candles → evidence | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Support/Resistance | `SupportResistanceEngine` | candles → risk target context | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Supply/Demand | `SupplyDemandEngine` | candles → evidence | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Liquidity | `LiquidityEngine` | OHLCV inference → risk context | inference/unavailable label | `test_deterministic.py` | CONNECTED_BUT_INCOMPLETE |
| Volume | `VolumeEngine` | OHLCV → evidence | missing volume is contextual | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Momentum | `MomentumEngine` | candles → evidence | insufficient history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Volatility | `VolatilityEngine` | candles → risk stop checks | missing ATR labelled | `test_deterministic.py` | CONNECTED_BUT_INCOMPLETE |
| Pattern Recognition | `PatternRecognitionEngine` | candles → evidence | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Candlestick | `CandlestickEngine` | candles → evidence | degraded history | `test_deterministic.py` | CONNECTED_AND_TESTED |
| Correlation | `CorrelationEngine` | benchmark → contextual evidence | degraded overlap/freshness | `test_integration_features.py` | CONNECTED_AND_TESTED |
| Multi-Timeframe | `MultiTimeframeEngine` | HTF/ITF/LTF → confluence/validation | degraded missing/stale/future | `test_integration_features.py` | CONNECTED_AND_TESTED |
| Evidence | `EvidenceEngine` | engine findings → confluence | empty family set | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Confluence | `ConfluenceEngine` | independent families → filter | no aligned evidence | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Opportunity Filter | `OpportunityFilter` | confluence/MTF → decision | ineligible | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Decision | `DecisionEngine` | eligible evidence → risk | `NO_TRADE`/`WAIT` | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Risk | `RiskEngine` | structure/SR/ATR/liquidity → validation | failed directional risk | `test_integration_features.py` | CONNECTED_AND_TESTED |
| Confidence | `ConfidenceEngine` | quality/families/MTF/risk → validation | low analytical confidence | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Validation | `ValidationEngine` | risk/MTF/freshness/confidence → result | failure becomes `NO_TRADE` | `test_freshness_telemetry.py` | CONNECTED_AND_TESTED |
| Explainability | `ExplainabilityEngine` | state → output | summary remains available | `test_pipeline.py` | CONNECTED_AND_TESTED |
| AI Reasoning | `AIReasoningLayer` | deterministic result → degraded AI output | no provider fallback | `test_pipeline.py` | CONNECTED_AND_TESTED |
| Strategy/Backtesting | `HistoricalBacktester` | production service → result | no validated trade | `test_backtesting.py` | CONNECTED_AND_TESTED |

## Related Documents

[Engine Dependency Model](../05-analysis/engine-dependency-model.md), [Engine Contract Standard](../05-analysis/engine-contract-standard.md), [Analysis Output Standard](../05-analysis/analysis-output-standard.md)

## Change History

- 2.1.0 - Recorded initial fixture-backed implementation status and remaining boundaries.
- 2.2.0 - Recorded verified MTF, risk/validation, and correlation runtime gates.
- 2.3.0 - Added freshness, conservative execution, and verified reachability matrix.
- 2.4.0 - Documented decision-state semantics, risk construction boundaries, and behavioral coverage.
- 2.0.0 - Finalized lifecycle, provenance, cost, and degraded behavior.
- 1.0.0 - Initial specification.

## Approval

Proposed; CTO approval required.
