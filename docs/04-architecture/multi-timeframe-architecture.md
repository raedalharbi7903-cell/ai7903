---
title: Multi-Timeframe Architecture
document_id: DOC-MTF-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Multi-Timeframe Architecture
## Purpose
Define timeframe architecture.
## Scope
Implemented three-input validation and deterministic alignment behavior.
## Main Content
The runtime accepts named `htf`, `itf`, and `ltf` inputs. Each is independently parsed, validated, required to provide at least five completed candles, and rejected if its latest completed candle is later than the primary decision timestamp. It runs the deterministic trend observation separately for each input and records provider, quality, source timestamp, and completed-candle timestamp in the result. Equal directional observations are `aligned`; otherwise they are `conflict`.

Missing, malformed, stale/future, or insufficient inputs result in degraded MTF output. Conflict and degraded/unavailable MTF prevent a directional decision from passing final validation. Timeframe hierarchy, weighting, aggregation, and production freshness thresholds remain Decision Required.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
- 1.1.0 — Documented verified three-timeframe runtime gate and limitations.
## Approval
Proposed; CTO approval required.
