---
title: Analysis Pipeline
document_id: DOC-ARCH-PIPELINE-001
version: 2.2.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
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

## Related Documents

[Engine Dependency Model](../05-analysis/engine-dependency-model.md), [Engine Contract Standard](../05-analysis/engine-contract-standard.md), [Analysis Output Standard](../05-analysis/analysis-output-standard.md)

## Change History

- 2.1.0 - Recorded initial fixture-backed implementation status and remaining boundaries.
- 2.2.0 - Recorded verified MTF, risk/validation, and correlation runtime gates.
- 2.0.0 - Finalized lifecycle, provenance, cost, and degraded behavior.
- 1.0.0 - Initial specification.

## Approval

Proposed; CTO approval required.
