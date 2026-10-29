---
title: Legacy Deterministic Methodology Review
document_id: DOC-ANALYSIS-LEGACY-REVIEW-001
version: 1.0.0
status: decision-required
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-29
related_documents: [DOC-ANALYSIS-CATALOG-001, DOC-ARCH-PIPELINE-001]
---

# Legacy deterministic methodology review

## Purpose

Distinguish verified calculations from incomplete methodology. File existence,
engine count and passing synthetic tests do not prove analytical independence.

## Scope

Current deterministic.py and related registered engines. This review does not
approve new formulas, evidence weights, confidence behavior or product strategy.

## Main content

| Component | Actual current methodology | Remaining limitation |
| --- | --- | --- |
| Market context | First/last close direction | No regime/session model; direction reused as a vote despite indirect catalogue responsibility |
| Market structure | Last-five first/last high/low comparison; range extrema | Not a complete confirmed-swing structural model; reported bias uses whole-prefix direction |
| Trend | Arithmetic 3/5 close averages checked against whole-prefix direction | Mixed/flat conditions and regime interpretation remain provisional |
| Support/resistance | Recent-five high/low range and proximity | No reaction-strength/confirmation model; whole-prefix direction is not level-derived directional evidence |
| Supply/demand | Same range labeled from whole-prefix direction | No documented zone formation/mitigation methodology |
| Liquidity | Adjacent equal-high counts and recent range | OHLCV inference only; whole-prefix direction is not independent liquidity evidence |
| Volume | Validated five-observation rolling baseline excluding current | Direction still inherited from price change; no separately justified directional vote |
| Momentum | One-period ROC and arithmetic-window RSI | RSI is not Wilder-smoothed; selected methodology requires explicit acceptance |
| Volatility | Arithmetic mean true range | Not Wilder-smoothed ATR; no independently validated regime thresholds |
| Pattern recognition | Latest-body/spread ratio | Not a complete pattern catalogue; context bias inherited from price |
| Candlesticks | Explicit geometry/engulfing boundaries and conflict handling | Context interpretation is limited; no guaranteed reversal |
| Correlation | Timestamp-aligned Pearson close-level correlation | Contextual, non-directional; not return correlation or causation |

### Corrected numerical defects

Positive integer periods and finite observations are now validated. Means avoid
overflowing intermediate sums; RSI uses a stable gain/loss ratio without changing
its arithmetic-window definition. Pearson correlation normalizes each series
before centering/products, preserving scale invariance at large/tiny magnitudes.
The pipeline rejects nonfinite output measurements rather than emitting nulls or
invalid JSON. Reference values and production failure paths have regression tests
in backend/tests/analysis/test_numeric_boundaries.py.

### Critical evidence-independence decision

Several nominal families currently inherit the same whole-prefix close direction.
Confluence correctly groups equal family names and rejects contradictions, but
that does not establish independence across different family names sharing a
directional calculation. Current family counts can therefore overstate distinct
analytical support. Existing duplicate-family tests do not close this issue.

Changing these contributions affects decision/confidence behavior and requires
CTO approval under the permanent red-level policy:

- Option A: keep context/levels/liquidity observations non-directional unless their
  own approved method establishes direction. Conservative; fewer executable fixture
  decisions; does not invent new inference algorithms.
- Option B: approve explicit directional contribution and dependency rules for each
  family before implementing them. More expressive; requires methodological design,
  calibration evidence and additional behavioral acceptance.

Recommendation: A as the immediate safety correction, followed by B only through
an approved methodology specification. No confidence weights, decision logic or
family taxonomy were changed by this review.

## Related documents

- [Engine catalogue](engine-catalog.md)
- [Evidence architecture](../04-architecture/evidence-architecture.md)
- [Requirement evidence](../10-testing/requirement-evidence-matrix.md)

## Change history

- 1.0.0 — Recorded actual methods, numerical fixes and unresolved independence issue.
