---
title: Analysis Output Standard
document_id: DOC-ANALYSIS-OUTPUT-001
version: 2.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-16
next_review: 2026-11-16
related_documents: [DOC-ANALYSIS-CATALOG-001, DOC-ARCH-DECISION-001]
---

# Analysis Output Standard

## Purpose

Define the canonical final analytical response and user-facing safety boundary.

## Scope

Response design only; no public API contract, trade execution, formula, or recommendation state is introduced.

## Main Content

A final response contains where applicable: instrument, market, provider/exchange, analyzed timeframes, market context, key findings, evidence references, confluence, decision, entry concept, invalidation, stop-loss concept, targets, risk/reward concept, confidence, conflicts, warnings, validation status, AI explanation, analysis timestamp, and data freshness. Every claim must trace to data → finding → evidence → confluence → decision and qualifiers. Missing data is explicit.

Decision is not a forecast. Risk independently describes invalidation, stop/target reasoning, adverse conditions, liquidity/volatility and no-trade concerns. Confidence is analytical confidence, not probability of profit unless statistically calibrated. Validation is the final PASS/FAIL/DEGRADED gate: PASS may proceed, FAIL blocks output, DEGRADED permits only qualified scope.

Explainability answers what was found, supporting evidence, conflicts, rationale, invalidation, risks, and confidence limits. AI receives only the validated explanation packet and may explain, summarize, contextualize uncertainty, and describe scenarios. It may not fabricate data, evidence, indicators, findings, signals, or overrides; bypass validation; or conceal uncertainty.

Use “Current evidence supports…”, “The analysis favors…”, “The setup is invalidated if…”, “Confidence is…”, “Conflicting evidence exists…”, and “No trade is recommended because…”. Never claim guaranteed, certain, risk-free, or definitive outcomes. This platform provides analysis/decision support and does not automatically execute trades unless separately approved and implemented.

## Related Documents

[Decision Architecture](../04-architecture/decision-architecture.md), [Risk Architecture](../04-architecture/risk-architecture.md), [Validation Architecture](../04-architecture/validation-architecture.md)

## Change History

- 2.0.0 - Finalized final-output, AI, validation, and trading boundary.
- 1.0.0 - Initial standard.

## Approval

Proposed; CTO approval required.
