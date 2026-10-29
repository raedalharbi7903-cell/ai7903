---
title: Backtesting Engine
document_id: DOC-ANALYSIS-BACKTESTING_ENGINE-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Backtesting Engine
## Purpose
Define the architectural responsibility of Backtesting Engine.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
Inputs require validated provenance, instrument, timeframe, timestamp, and context. Outputs require attributable findings, evidence, status, warnings/errors, downstream-consumer traceability, and validation. Dependencies, timeframe/instrument behavior, failure behavior, and exact algorithms are Decision Required; this document does not implement the engine.

**Implemented:** documentation only. **Approved Future Architecture:** this subject may be implemented only through approved work. **Decision Required:** exact algorithms, formulas, providers, permissions, and operational thresholds are not approved unless stated otherwise.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
## Approval
Proposed; CTO approval required.

## Runtime implementation update — 2026-10-29

The historical design-only status above no longer describes all runtime code.
HistoricalBacktester now invokes AnalysisService on sequential prefixes. Optional
explicit timeframe snapshots are cut at decision time; no primary series is cloned
into HTF/ITF/LTF. Frames require distinct ordered intervals and matching provenance.
Missing confirmation means no executable trade.

The evaluator opens BUY spot-long simulations only; SELL does not open a short.
The implemented assumptions are decision-close entry and one-bar holding, with
stop-first resolution when stop and target both cross. Adverse opening gaps worsen
stop fills, slippage applies at entry and exit, and fees use both notionals.
Unsupported timing policies and invalid cost/geometry values are rejected.
Returns are summed one-bar returns, not a compounded portfolio performance claim.
Versions and cost settings are included in results. Development/OOS data must be
strictly chronological; no empirical confidence calibration is claimed.
Tests: backend/tests/analysis/test_historical_acceptance.py and test_backtesting.py.
