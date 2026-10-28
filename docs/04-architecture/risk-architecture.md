---
title: Risk Architecture
document_id: DOC-RISK-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-DECISION-ARCH-001]
---
# Risk Architecture
## Purpose
Define risk as a distinct analysis responsibility.
## Scope
Implemented structural-risk gate; position sizing and execution policy remain out of scope.
## Main Content
For a directional decision, the runtime derives an invalidation from market structure. BUY invalidation must be below price; SELL invalidation must be above price. It produces stop, target, positive risk distance, risk/reward, and risk-quality metadata. The target is set at two risk units, and a metadata-configurable minimum risk/reward (default 1.0) is enforced. Invalid, unavailable, or insufficient structural risk fails validation and returns `NO_TRADE` in the public analysis result.

This is an analytical gate, not position sizing, trading execution, or a recommendation. Volatility/liquidity-adjusted levels and production risk policy remain Decision Required.
## Related Documents
[Decision Architecture](decision-architecture.md)
## Change History
- 1.0.0 — Initial risk boundary.
- 1.1.0 — Documented verified structural-risk validation gate.
## Approval
Proposed; CTO approval required.
