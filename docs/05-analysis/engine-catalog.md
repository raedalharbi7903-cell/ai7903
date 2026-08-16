---
title: Engine Catalogue
document_id: DOC-ANALYSIS-CATALOG-001
version: 2.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-16
next_review: 2026-11-16
related_documents: [DOC-ANALYSIS-PHILOSOPHY-001, DOC-ARCH-PIPELINE-001]
---

# Engine Catalogue

## Purpose

Define the canonical 24-component analytical brain without overlapping responsibilities.

## Scope

Design only. No component algorithm, provider, numerical threshold, formula, or trading behavior is implemented or approved.

## Main Content

### Canonical component map

1. **Data Engine** — data/context.
2. **Market Context Engine** — data/context.
3. **Market Structure Engine** — deterministic.
4. **Trend Engine** — deterministic.
5. **Support & Resistance Engine** — deterministic.
6. **Supply & Demand Engine** — deterministic.
7. **Liquidity Engine** — deterministic.
8. **Volume Engine** — deterministic.
9. **Momentum Engine** — deterministic.
10. **Volatility Engine** — deterministic.
11. **Pattern Recognition Engine** — deterministic.
12. **Candlestick Engine** — deterministic.
13. **Correlation Engine** — deterministic.
14. **Multi-Timeframe Engine** — aggregation.
15. **Evidence Engine** — aggregation.
16. **Confluence Engine** — aggregation.
17. **Opportunity Filter** — aggregation.
18. **Decision Engine** — decision/risk.
19. **Risk Engine** — decision/risk.
20. **Confidence Engine** — decision/risk.
21. **Validation Engine** — decision/risk.
22. **Explainability Engine** — explanation/AI.
23. **AI Reasoning Layer** — explanation/AI.
24. **Strategy & Backtesting System** — strategy/evaluation.

### Component implementation specifications

#### Data Engine

- **Purpose/responsibility:** validate, normalize, snapshot and provenance-tag raw data.
- **Non-responsibility:** No market inference.
- **Inputs → outputs:** provider data → validated snapshot, quality/freshness/provenance; produced contribution: indirect.
- **Upstream dependencies:** none. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** all; instrument applicability and data availability must be explicit.
- **Operation:** stateful snapshot; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** indirect; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Market Context Engine

- **Purpose/responsibility:** describe applicable regime, session and instrument conditions.
- **Non-responsibility:** No directional decision.
- **Inputs → outputs:** validated snapshots → context profile; produced contribution: indirect.
- **Upstream dependencies:** Data. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** higher/requested; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** indirect; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Market Structure Engine

- **Purpose/responsibility:** identify structural price relationships.
- **Non-responsibility:** No trend or momentum measurement.
- **Inputs → outputs:** data/context → structure findings/invalidation; produced contribution: evidence only.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** multi-timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Trend Engine

- **Purpose/responsibility:** describe directional persistence.
- **Non-responsibility:** No structure-break or momentum decision.
- **Inputs → outputs:** data/context/structure → trend findings/invalidation; produced contribution: evidence only.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Support & Resistance Engine

- **Purpose/responsibility:** identify reaction levels/zones.
- **Non-responsibility:** No supply/demand or liquidity inference.
- **Inputs → outputs:** data/structure → level findings/invalidation; produced contribution: evidence only.
- **Upstream dependencies:** Data, Structure. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Supply & Demand Engine

- **Purpose/responsibility:** identify documented supply/demand zones.
- **Non-responsibility:** No support/resistance duplication.
- **Inputs → outputs:** data/structure → zone findings/state; produced contribution: evidence only.
- **Upstream dependencies:** Data, Structure. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P2.

#### Liquidity Engine

- **Purpose/responsibility:** assess tradability/liquidity observations.
- **Non-responsibility:** No directional intent.
- **Inputs → outputs:** data/context → liquidity constraints/warnings; produced contribution: eligibility/risk evidence.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** instrument/timeframe aware; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** eligibility/risk evidence; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Volume Engine

- **Purpose/responsibility:** interpret available volume observations.
- **Non-responsibility:** No momentum substitute.
- **Inputs → outputs:** volume-capable data/context → volume findings; produced contribution: evidence only.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P2.

#### Momentum Engine

- **Purpose/responsibility:** describe directional impulse.
- **Non-responsibility:** No trend/volatility or independent indicator voting.
- **Inputs → outputs:** data/context → momentum-family findings; produced contribution: evidence only.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P2.

#### Volatility Engine

- **Purpose/responsibility:** describe variability/range conditions.
- **Non-responsibility:** No trend/momentum inference.
- **Inputs → outputs:** data/context → volatility/risk findings; produced contribution: risk/context evidence.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** risk/context evidence; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Pattern Recognition Engine

- **Purpose/responsibility:** identify approved multi-bar/structure patterns.
- **Non-responsibility:** No single-candle classification.
- **Inputs → outputs:** data/structure → pattern findings; produced contribution: evidence only.
- **Upstream dependencies:** Data, Structure. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P3.

#### Candlestick Engine

- **Purpose/responsibility:** identify limited-candle observations.
- **Non-responsibility:** No broader pattern decision.
- **Inputs → outputs:** OHLC/context → candle findings; produced contribution: supporting evidence.
- **Upstream dependencies:** Data, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** per timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** supporting evidence; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P3.

#### Correlation Engine

- **Purpose/responsibility:** describe supported inter-instrument relationships.
- **Non-responsibility:** No standalone context/direction.
- **Inputs → outputs:** aligned snapshots → relationship findings; produced contribution: context evidence.
- **Upstream dependencies:** Data. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** aligned frames; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** context evidence; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P3.

#### Multi-Timeframe Engine

- **Purpose/responsibility:** align source findings across hierarchy.
- **Non-responsibility:** No source recalculation or voting.
- **Inputs → outputs:** findings by timeframe → alignment/conflicts/coverage; produced contribution: evidence only.
- **Upstream dependencies:** Analysis engines, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** higher=context; lower=timing; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** evidence only; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Evidence Engine

- **Purpose/responsibility:** normalize validated findings into evidence.
- **Non-responsibility:** No confluence/decision scoring.
- **Inputs → outputs:** validated findings → evidence ledger/families/conflicts; produced contribution: indirect.
- **Upstream dependencies:** Analysis engines. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** preserves source; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** indirect; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Confluence Engine

- **Purpose/responsibility:** assess agreement across independent dimensions.
- **Non-responsibility:** No indicator counting/decision.
- **Inputs → outputs:** evidence/context/timeframes → confluence/gaps/conflicts; produced contribution: decision prerequisite.
- **Upstream dependencies:** Evidence, MTF, Context. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** cross-timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** decision prerequisite; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Opportunity Filter

- **Purpose/responsibility:** admit/reject unsuitable analysis opportunities.
- **Non-responsibility:** No buy/sell direction.
- **Inputs → outputs:** quality/liquidity/context/confluence → eligible/rejected/deferred reason; produced contribution: downstream gate.
- **Upstream dependencies:** Data, Context, Liquidity, Confluence. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** requested set; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** downstream gate; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Decision Engine

- **Purpose/responsibility:** produce traceable analytical state.
- **Non-responsibility:** No profit forecast/risk calculation.
- **Inputs → outputs:** eligible confluence/conflicts → state/rationale/scenarios; produced contribution: direct.
- **Upstream dependencies:** Confluence, Filter, Evidence. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** uses MTF; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** direct; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Risk Engine

- **Purpose/responsibility:** describe invalidation/adverse/risk-reward concepts.
- **Non-responsibility:** No direction or confidence.
- **Inputs → outputs:** decision/context/volatility/liquidity → risk/warnings/stop-target concepts; produced contribution: direct qualifier.
- **Upstream dependencies:** Decision candidate, Volatility, Liquidity. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** timeframe aware; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** direct qualifier; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Confidence Engine

- **Purpose/responsibility:** express analytical confidence, not profit probability.
- **Non-responsibility:** No validation/risk replacement.
- **Inputs → outputs:** quality/confluence/conflict/risk → confidence factors/limits; produced contribution: direct qualifier.
- **Upstream dependencies:** Evidence, Confluence, Risk. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** cross-timeframe; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** direct qualifier; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### Validation Engine

- **Purpose/responsibility:** gate data through final integrity checks.
- **Non-responsibility:** No repair/fabrication.
- **Inputs → outputs:** all upstream outputs → PASS/FAIL/DEGRADED; produced contribution: mandatory gate.
- **Upstream dependencies:** all. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** all; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** mandatory gate; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P0.

#### Explainability Engine

- **Purpose/responsibility:** deterministically prepare traceable explanation inputs.
- **Non-responsibility:** No new findings/advice.
- **Inputs → outputs:** validated structures → explanation packet/citations; produced contribution: indirect.
- **Upstream dependencies:** Validation, Evidence, Decision, Risk, Confidence. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** preserves source; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** indirect; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P1.

#### AI Reasoning Layer

- **Purpose/responsibility:** communicate validated explanation in human language.
- **Non-responsibility:** No fabrication/override/bypass.
- **Inputs → outputs:** validated explanation packet → bounded narrative; produced contribution: indirect.
- **Upstream dependencies:** Explainability, Validation. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** supplied frames only; instrument applicability and data availability must be explicit.
- **Operation:** stateless; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** indirect; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P2.

#### Strategy & Backtesting System

- **Purpose/responsibility:** define/evaluate versioned strategies offline.
- **Non-responsibility:** Not a real-time engine or decision input.
- **Inputs → outputs:** rules/historical data → evaluation and calibration results; produced contribution: never direct.
- **Upstream dependencies:** historical data. **Downstream consumers:** declared next pipeline consumers; no implicit dependencies.
- **Timeframe, instrument, data:** market/frame-specific; instrument applicability and data availability must be explicit.
- **Operation:** stateful runs; independently operable only with valid dependencies; failures return explicit unavailable, failed, or degraded status, warnings, provenance, and invalidation conditions.
- **Decision/calibration/priority:** never direct; numeric methods and thresholds are **CALIBRATION REQUIRED**; implementation priority P3.

### Status

**APPROVED / EXISTING:** component categories, deterministic-first boundary, provenance, validation gate, and AI-after-validation position. **DECISION REQUIRED:** providers, markets, instruments, final decision vocabulary, and strategy scope. **CALIBRATION REQUIRED:** every weight, threshold, formula choice, conflict severity, and eligibility rule. **IMPLEMENTATION REQUIRED:** calibrated algorithms, live providers, multi-timeframe inputs, production AI integration, and offline historical evaluation. The initial fixture-backed component pipeline is implemented and tested; its empirical behavior remains provisional.

## Related Documents

[Engine Contract Standard](engine-contract-standard.md), [Engine Dependency Model](engine-dependency-model.md), [Analysis Output Standard](analysis-output-standard.md)

## Change History

- 2.1.0 - Recorded initial fixture-backed implementation status.
- 2.0.0 - Finalized canonical 24-component responsibility map.
- 1.0.0 - Initial catalogue.

## Approval

Proposed; CTO approval required.
