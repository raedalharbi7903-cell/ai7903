---
title: Backtesting
document_id: DOC-10-BACKTESTING-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Backtesting
## Purpose
Define standards for Backtesting.
## Scope
Fixture-compatible sequential historical evaluation; empirical performance claims remain out of scope.
## Main Content
`HistoricalBacktester.run_pipeline()` invokes the production `AnalysisService` with a candle prefix ending at each decision candle. The following candle is used only after the decision for simulated return evaluation. Only validation-passing decisions may enter a simulated trade. Fees and slippage are configurable; results retain dataset identity, strategy/parameter versions, analysis version, decision history, and validated-decision count.

This is infrastructure for deterministic fixture testing, not a claim of strategy profitability or historical validity. Same-candle stop/target resolution, approved datasets, provider rights, execution timing policy, and empirical performance methodology remain Decision Required.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
- 1.1.0 — Documented verified production-pipeline backtest path and boundaries.
## Approval
Proposed; CTO approval required.
