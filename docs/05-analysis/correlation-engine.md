---
title: Correlation Engine
document_id: DOC-ANALYSIS-CORRELATION_ENGINE-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Correlation Engine
## Purpose
Define the architectural responsibility of Correlation Engine.
## Scope
Architecture, governance, and the implemented fixture-compatible correlation behavior.
## Main Content
Inputs require validated provenance, instrument, timeframe, timestamp, and context. Outputs require attributable findings, evidence, status, warnings/errors, downstream-consumer traceability, and validation.

The current runtime implementation accepts benchmark candles through analysis metadata, parses them as OHLCV, excludes records after the primary decision time, and joins both series by timestamp. It calculates Pearson correlation on aligned closes only; fewer than three aligned points produces a degraded output. Output includes sample size, methodology, and benchmark-provider provenance.

Correlation is contextual information only. Its evidence carries no bullish/bearish bias and cannot create an independent directional confirmation or inflate confluence/confidence. Instrument selection, live-provider permissions, operational thresholds, and any predictive use remain Decision Required.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
- 1.1.0 — Documented timestamp-aligned contextual runtime behavior.
## Approval
Proposed; CTO approval required.
