---
title: Founder Decisions and Approval Precedence
document_id: DOC-HANDOVER-DECISIONS-001
version: 1.0.0
status: approved-requirements-not-implementation
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-HANDOVER-001, DOC-HANDOVER-DECISIONS-001]
---

# Founder decisions

## Purpose

Preserve the approved product direction for the next Goal without implying delivery.

## Scope

Approval source: founder's **MASTER CTO DIRECTIVE — SAFE PROJECT HANDOVER & GOAL
REPLACEMENT**, attachment 925afff4-fe80-47a7-9067-1d21423f1db4, received 2026-10-30.
Identity/infrastructure clarifications also arrived as direct founder replies.
Option A approval is recorded in the existing acceptance register.
This is an approval record, not a redesign or an instruction to implement new
features during handover. Earlier historical records remain intact.

## Main content

### Approved requirement register

| ID | Approved requirement | Current implementation / consequence |
| --- | --- | --- |
| FD01 | Saudi-first AI technical-analysis platform; Arabic-first customer experience | Current English fixture UI is not Arabic-first acceptance |
| FD02 | Cryptocurrency spot analysis first; other markets only in later approved phases | Current spot fixture boundary retained; no new market integration authorized here |
| FD03 | Analyze only on explicit customer request | Current submit-driven demo; retain this requirement in future routes/jobs |
| FD04 | No automatic customer opportunity scanning or proactive trading-opportunity alerts | No such product runtime found; do not add a scanner/alert product by inference |
| FD05 | No automated trade execution | SELL is analytical direction, not short execution or an executable order |
| FD06 | No customer-facing interactive AI chat | Founder executive Board Meeting below is a separate, explicitly approved context |
| FD07 | AI explains deterministic results and cannot override safety | Provider unavailable/degraded today; do not fabricate narrative or certainty |
| FD08 | Launch pricing deferred until actual operating cost per customer is measured | 169 SAR is NOT an approved final launch price; preserve flexible pricing, no fixed-price production assumption |
| FD09 | Exactly eleven Command Center top-level sections, listed below | All eleven are approved requirements, not implemented dashboards |
| FD10 | AI CTO nested inside Engineering Center; AI CFO inside Financial Center | Do not create additional top-level CEO/CTO/CFO sections beyond the approved list |
| FD11 | Analytical health in Intelligence Health; operational health in Mission Control | Existing telemetry is only a foundation, not either complete section |
| FD12 | Board Meeting is independent section eleven | Weekly interactive text executive meetings with minutes, decisions and follow-up actions; not implemented |
| FD13 | Command Center exclusive to one founder; no employee/delegated initial access | Internal issuer+subject+MFA boundary exists; real administration absent |
| FD14 | Sensitive decisions require founder approval | Reporting/monitoring may automate only low-risk tasks with explicitly defined permissions; no blanket agent authority |
| FD15 | Email-based customers; founder MFA; secure sessions/recovery/least privilege/auditable sensitive operations | Vendor and credential/recovery flow remain subject to security/cost review |
| FD16 | PostgreSQL intended production DB; separate development/testing/production | No PostgreSQL acceptance evidence yet; existing disposable SQLite tests preserved |
| FD17 | Provider-neutral design where appropriate | No specific AI model/vendor, authentication vendor or paid hosting selected |
| FD18 | No unauthorized paid commitments or external customer-data transfer | No purchases/contracts/services/data transfers performed during handover |
| FD19 | Feature branch only; no merge or main push | Continue feature/crypto-analysis-validation unless separately authorized |

### Exactly eleven Command Center sections

1. Executive Overview
2. AI CEO Brief
3. Intelligence Health
4. Engineering Center
5. Financial Center
6. Product Intelligence
7. Research Lab
8. Evolution Center
9. Decision Center
10. Mission Control
11. Board Meeting

AI CTO belongs inside section 4; AI CFO inside section 5. Board Meeting is a
separate eleventh section. Sensitive executive decisions remain founder-gated.
Neither these names nor the approval establish implemented AI agents, data access
permissions, account actions, meeting persistence or production dashboards.

### Unresolved decisions / approvals

Authentication vendor and exact email credential/session/recovery/MFA lifecycle;
AI provider/model and privacy/data-sharing constraints; licensed data providers and
datasets; detailed administrative/agent action permissions; measured costs and final
pricing; Saudi processor/recurring billing/invoicing/refund/cancellation details;
hosting/database backup/RPO/RTO/domain/release approvals; qualified Saudi regulatory,
privacy, commercial and tax review. See the external register in REMAINING_WORK.md.

### Historical conflict and precedence register

| Record | Conflict / obsolete assertion | Safe interpretation and next action |
| --- | --- | --- |
| docs/01-project/project-manifest.md | Early exclusions include accounts/payments/dashboards/analysis | Historical sprint/proposed scope, not a rejection of the newer explicitly approved product; do not rewrite Manifest during handover |
| docs/02-product/product-requirements.md; product-scope.md; mvp-definition.md | Broad markets/features/users still Decision Required; foundations-only wording | FD01-FD19 resolve the stated direction, not unspecified detailed contracts; use this register and inventory |
| docs/02-product/out-of-scope.md; product-boundaries.md | Accounts/indicators/recommendations absent or excluded at earlier stage | Preserve historical evidence, distinguish no trading execution from future approved analysis/accounts/billing |
| docs/04-architecture/architecture-baseline.md; system-overview.md | Evidence/decision/confidence/frontend described as future/unimplemented | Runtime service/API/React and tests now exist; baseline remains historical proposed design, not current status |
| docs/04-architecture/frontend-architecture.md | React only on a separate sprint branch; product UI unimplemented | Current feature branch has a working fixture UI, but not Arabic/live/customer authentication |
| docs/07-organization/approval-matrix.md | Administrative/site roles unrecoverable | FD13/FD15 now resolve the initial access model; detailed sensitive-action permissions still require review |
| docs/10-testing/requirement-evidence-matrix.md | Several old counts and CI pending/failure statements coexist | Dated historical observations; use current handover evidence by SHA, not isolated old lines |
| docs/05-analysis/engine-catalog.md; legacy-methodology-review.md | Proposed algorithms/status language can appear more mature than code; some pre-Option-A descriptions remain | Inventory documents actual methods and limitations; null contextual contributions are approved/implemented; no empirical independence claimed |
| Proposed 169 SAR price mentioned by founder | No final approved pricing evidence; no 169 entry found in inspected current pre-handover product docs/runtime | Preserve founder's explicit deferral; any historical proposal must not become runtime launch pricing |
| Early unknown founder roles in PROGRESS.md/PROJECT_SPEC.md | Chronological older sections precede explicit identity approval | New dated approval overlay controls; retain old entries as history |
| Vendor URLs/defaults in .env.example/settings; OkxProvider | Configuration/source existence may look like commercial provider approval | Defaults/adapters do not confer rights; public API remains fixture-only; vendor licensing still unresolved |

Proposed documents without approval evidence do not authorize detailed formulas,
prices, thresholds, autonomous agent powers or additional product scope.
No approval is inferred from a file's existence or an old status heading.
A newer explicit founder decision controls the listed conflict; unresolved details
remain Decision Required and require traceable approval before behavior changes.

## Related documents

- [Project handover](PROJECT_HANDOVER.md)
- [Implementation inventory](IMPLEMENTATION_STATUS.md)
- [Remaining work and external dependencies](REMAINING_WORK.md)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [Acceptance register](../03-engineering/acceptance-dependencies.md)

## Change history

- 1.0.0 — Preserved the explicit founder direction and listed historical conflicts.
