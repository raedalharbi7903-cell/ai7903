---
title: Grounded Arabic Deterministic Explanation
document_id: DOC-AR-EXPLANATION-001
version: 1.0.0
status: partial-deterministic-fallback
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-EXPLAIN-001, DOC-AI-REASONING-001]
---

# Grounded Arabic explanation

## Purpose

Explain final deterministic decisions in Arabic without external AI or invented
market facts. This is a safe fallback, not a completed generative AI integration.

## Scope

Existing ExplainabilityEngine output gains optional data.arabic_explanation.
Top-level contract 1.0, legacy summary, five decisions and existing API fields remain.
No new public endpoint, provider, request parameter or analytical algorithm.

## Main content

explanations.py reads final decision/validation, existing evidence and actual fixture
status. Typed output has methodology_version deterministic-ar-v1, language ar,
mode deterministic_fallback, decision, validation, fixed summary, limitations and
source evidence references. It never mutates context or adds evidence/votes.

Fixed Arabic sentences distinguish SELL from opening a short; NO_TRADE, WAIT and
INSUFFICIENT_DATA are never described as executable recommendations. Missing data
and failed/degraded validation remain unavailable/non-actionable. Limitations state
that this is deterministic, confidence is not profit probability, and fixtures are
synthetic when applicable. No new price, indicator, numerical confidence or outcome
is generated. Free-form findings/provider strings are not interpolated into prose;
instructions or guarantees embedded in them cannot alter these fixed statements.
This does not certify prompt-injection defenses of a future external language model.

References point to actual evidence IDs/engines/families, classed contextual,
supporting or conflicting against existing final direction/conflicts. Opposed
directional families are not concealed when final decision is NO_TRADE.
Multiple references are not independent votes; confluence/confidence are unchanged.
No empirical independence/calibration claim is added.

Pipeline final failure reconciliation rebuilds both legacy and Arabic explanations.
A failure after the explanation stage cannot leave an actionable Arabic summary.
Frontend checks supported version/language/mode and exact final decision/validation
before rendering prose. A stale/malformed Arabic payload is withheld, not shown as
raw JSON. Older responses without the optional object keep legacy display.
React renders ordinary text, not HTML. No new visual palette/font/layout chosen.

AIReasoningLayer still reports available false/degraded; this is not AI-generated
text, a selected provider, a paid commitment, or approval to transfer customer data.
There is no remote invocation, customer chat, cost estimate or fabricated SLA.

## Verification and remaining work

backend/tests/analysis/test_arabic_explanation.py covers all five actual service
states, late failures, malicious source prose, conflicts, fixture labeling,
state immutability and degraded validation. Existing safety/failure regressions pass.
frontend/src/types/explanation.test.ts checks compatible/malformed/stale contracts;
AnalysisResults.test.tsx rejects stale claims; analysis.integration.test.tsx
proves actual React → HTTP API → existing service → Arabic result rendering.

Remaining: richer approved reason-code translations, reference presentation,
reviewed Arabic copy/accessibility/browser/visual acceptance, approved AI provider
and privacy controls, provider failure/cost/prompt-injection acceptance. No
generative AI or full explainability completion claim.

## Related documents

- [Explainability architecture](../04-architecture/explainability-architecture.md)
- [AI architecture](../04-architecture/ai-reasoning-architecture.md)
- [Canonical requirements](../02-product/canonical-requirements.json)
- [Delivery](../delivery/b1-arabic-explanation-delivery.md)

## Change history

- 1.0.0 — Grounded deterministic Arabic fallback in existing pipeline and frontend.

