---
title: Arabic RTL Functional Foundation
document_id: DOC-UI-ARABIC-001
version: 1.0.0
status: partial-functional-foundation-design-pending
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001, DOC-FRONTEND-DESIGN-001]
---

# Arabic/RTL workflow

## Purpose

Implement the approved Arabic-first functional foundation without finalizing visuals.

## Scope

UI-ARABIC / G07 and approved customer analysis workflow. Synthetic API mode only.
This is not complete customer accounts/history/billing/support or approved visual design.

## Main content

Arabic functional copy is centralized in frontend/src/i18n/ar.ts. Layout and HTML
declare Arabic/RTL; pair input and technical JSON remain LTR; bidi isolation keeps
provider/instrument identifiers intact. CSS uses logical start/end spacing and
skip navigation targets a focusable main landmark.
The inherited font stack/colors remain provisional; no Arabic font or final
theme/brand/mobile presentation was selected.

All five decision labels, confidence/uncalibrated labels, panels, form, loading,
empty/error and missing-page copy are Arabic. Numerical confidence outside the
approved low/medium/high qualitative vocabulary is withheld rather than shown as
probability. Nonfinite/absent values are unavailable. Source identifiers are not
translated even if their names match a confidence word.
Aware timestamps are normalized to explicit UTC; naive/invalid timestamps are
unavailable instead of inventing a timezone.

Unknown source observations, warning strings, engine field keys and raw technical
details may remain English. They are source material, not fabricated Arabic AI
explanations. Complete grounded Arabic explanations and final copy/legal review
remain open. SELL remains analysis only, not short execution or an order.
No business/analytical/API contract changed.

The client now normalizes HTTP, network and malformed-response failures into safe
Arabic errors. Raw response bodies/native exception messages never reach the UI.
Actual response parsing remains strict. Tests cover private error payloads,
on-demand-only behavior, accessible names/RTL/LTR, qualitative confidence, UTC,
all decisions and the actual React/FastAPI/service integration.
An initial integration assertion matched two translated classification fields;
it now targets the actual classification element without weakening its value check.

A missing root .editorconfig was restored using historical Sprint 1A.1 content
as evidence and corrected to include JSON/TS/etc two-space defaults, Python four
spaces, UTF-8/LF/newline/trailing-whitespace rules and Makefile tabs. Historical
Markdown trailing-space exception was not copied because the approved requirement
asks to trim trailing whitespace. No bulk reformat of existing source occurred.

Frontend suite: 30 PASS; TypeScript/ESLint/Prettier/build PASS.
Tooling suite: 23 PASS. Backend/application database code unchanged from verified
12e22e1; no unnecessary backend full-suite rerun for this frontend/docs package.
Hosted C2 evidence is retained separately. No desktop/tablet/mobile browser
visual acceptance or comprehensive accessibility certification is claimed.
All ten founder visual approvals remain pending.

## Related documents

- [Canonical requirements](../02-product/canonical-requirements.json)
- [Design approval](founder-design-approval.md)
- [PostgreSQL evidence](../10-testing/postgresql-acceptance-evidence.json)
- [Frontend setup](../../frontend/README.md)

## Change history

- 1.0.0 — Arabic/RTL functional flow, safe errors and explicit unapproved-design boundary.
