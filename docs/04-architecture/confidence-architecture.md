---
title: Confidence Architecture
document_id: DOC-CONFIDENCE-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-DECISION-ARCH-001]
---
# Confidence Architecture
## Purpose
Define confidence limitations.
## Scope
Implemented analytical-quality confidence layer; empirical calibration remains out of scope.
## Main Content
Confidence communicates evidence quality, agreement, data quality, timeframe alignment, uncertainty, and limitations. It is not probability of profit unless a validated statistical model is approved.

The implemented `analytical-quality-v1` method uses independent evidence-family count, confluence, primary data quality, MTF state, and structural-risk availability. It records explicit penalties for degraded data, unavailable/conflicting MTF, and unavailable/failed risk. Related evidence is counted by family rather than by indicator count, preventing duplicate momentum-style outputs from inflating independent confluence. Labels are `low`, `medium`, or `high`; all are emitted with calibration status `uncalibrated`.

Validation requires confidence output presence. Confidence remains an analytical quality label, not an empirical probability or profitability claim.
## Related Documents
[Decision Architecture](decision-architecture.md)
## Change History
- 1.0.0 — Initial confidence boundary.
- 1.1.0 — Documented verified analytical-quality implementation and calibration boundary.
## Approval
Proposed; CTO approval required.
