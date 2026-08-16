---
title: Engine Contract Standard
document_id: DOC-ANALYSIS-ENGINE_CONTRACT_STANDARD-001
version: 2.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-16
next_review: 2026-11-16
related_documents: [DOC-ANALYSIS-CATALOG-001, DOC-ARCH-EVIDENCE-001]
---

# Engine Contract Standard

## Purpose

Define the canonical result and evidence contract for deterministic components.

## Scope

No serialization schema or scoring formula is prescribed.

## Main Content

Every engine result carries: engine ID/name/version; instrument, market and provider/exchange where supplied; timeframe; analysis/source timestamps; freshness; input provenance; status; findings; evidence; warnings; errors; dependencies; and invalidation conditions. Inputs must be attributable and validated. Outputs must be traceable and never silently successful.

Evidence is first-class: evidence ID, source engine/version and observation, instrument, timeframe, timestamp, freshness, finding, directional bias where applicable, strength, quality, reliability, provenance, supporting observations, invalidation, conflicts, and independence/correlation classification.

Raw data is a provider snapshot. An indicator value is a tool output. A finding is a deterministic interpretation. Evidence is normalized traceable support. Confluence assesses independent agreement. A decision is a governed state. A recommendation is a user-facing expression only after validation. AI explanation is bounded language over validated structures.

Evidence quality considers data quality, freshness, completeness, source reliability, clarity, timeframe relevance, independence, contradiction, historical validation, and regime relevance. Numerical scoring is **CALIBRATION REQUIRED**. Correlated/derived indicators belong to evidence families and cannot be counted as independent confirmations; classify evidence as primary, supporting, duplicate, derived, or independent.

## Related Documents

[Engine Catalogue](engine-catalog.md), [Evidence Architecture](../04-architecture/evidence-architecture.md)

## Change History

- 2.0.0 - Finalized traceability, evidence, and independence contract.
- 1.0.0 - Initial specification.

## Approval

Proposed; CTO approval required.
