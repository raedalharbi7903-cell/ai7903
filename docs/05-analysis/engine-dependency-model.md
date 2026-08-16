---
title: Engine Dependency Model
document_id: DOC-ANALYSIS-ENGINE_DEPENDENCY_MODEL-001
version: 2.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-16
next_review: 2026-11-16
related_documents: [DOC-ANALYSIS-CATALOG-001, DOC-ARCH-PIPELINE-001]
---

# Engine Dependency Model

## Purpose

Define execution order, component boundaries, conflict handling, and failure propagation.

## Scope

Architecture only; the generic pipeline is framework support, not a concrete implementation.

## Main Content

### Order

Data → quality/normalization → Market Context → deterministic engines → Multi-Timeframe → Evidence → Confluence → Opportunity Filter → Decision → Risk → Confidence → Validation → Explainability → AI Reasoning → final analysis. Correlation enriches context after aligned data. Strategy/Backtesting is offline only.

### Boundaries

This is not an indicator aggregation or indicator-voting system. Indicators may support findings, but correlated indicators do not become independent decision authorities.

Structure describes relationships; Trend describes directional persistence; Momentum describes impulse; Volatility describes variability. Support/Resistance identifies reaction levels; Supply/Demand identifies separate zone semantics; Liquidity assesses tradability. Candlestick is limited-candle observation; Pattern is broader formation. Volume is participation, not Momentum. Correlation is relationship evidence; Context interprets it. Evidence is atomic support; Confluence judges independent agreement; Decision consumes prerequisites; Risk qualifies exposure; Confidence qualifies analytical certainty; Validation gates integrity; Explainability transforms deterministically; AI communicates only supplied facts.

### Conflict, no-trade, and degraded modes

Classify conflict by evidence family, source, timeframe, context relevance, and severity. Do not vote-count. Severe conflict, stale/partial data, insufficient independent evidence, unsuitable liquidity, invalid context, missing timeframes, failed risk prerequisites, or validation failure can legitimately yield NO TRADE, INSUFFICIENT DATA, or WAIT/DEFERRED. Exact thresholds/states are **DECISION REQUIRED / CALIBRATION REQUIRED**. Provider/data failures block dependents. Partial results may continue only as clearly labeled DEGRADED output; validation failure blocks final output. AI failure returns the validated deterministic result with an explicit AI-status warning.

## Related Documents

[Analysis Pipeline](../04-architecture/analysis-pipeline.md), [Conflict Resolution](../04-architecture/conflict-resolution.md), [Degraded Analysis Policy](../04-architecture/degraded-analysis-policy.md)

## Change History

- 2.0.0 - Finalized order, boundaries, and failure propagation.
- 1.0.0 - Initial model.

## Approval

Proposed; CTO approval required.
