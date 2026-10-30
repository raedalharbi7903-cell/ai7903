---
title: Remaining Work and External Dependency Register
document_id: DOC-HANDOVER-GAPS-001
version: 2.0.0
status: verified-scope-product-incomplete
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-HANDOVER-001, DOC-HANDOVER-DECISIONS-001]
---

# Remaining work

## Current gap overlay — 2026-10-30

The G01–G20 and EXT registers below retain stable gap IDs and historical detail.
Their original evidence predates later implementation. Apply these updates:

- G01/G02: provider-neutral acquisition exists; direct unapproved provider access
  is denied. Licensed retrieval/rights/coverage still unresolved.
- G07: Arabic RTL functional analysis, public guidance and history now exist.
  Final terminology/disclosures/design/browser/accessibility acceptance remains.
- G08: pinned Psycopg and owned PostgreSQL migration/transaction/dump-restore CI
  now exist, not production provisioning. Source-specific receipts are in CURRENT_STATE.
- G09: grounded Arabic deterministic fallback exists, not an external AI adapter.
- G15/G16: previously pending atomic history/audit save/delete is preserved with
  default-off policies and exact Origin checks. Full audit export/retention/abuse/
  vendor-session/production privacy acceptance is still missing.
- G20: the 101 grouped canonical records/reverse references and CI action policy
  now exist. Historical contradictions remain explicitly dated. No .editorconfig
  is claimed delivered merely because its historical version is recoverable.

[Current state](CURRENT_STATE.md) contains the actionable next-task delta,
acceptance evidence and all 23 customer workflow classifications. No implementation
work is authorized by this handover itself. The next Goal must reconcile these
updates rather than rebuilding the already verified foundations.

## Purpose

Provide an actionable backlog that preserves missing scope without repeating
completed work or mistaking approval for implementation.

## Scope

Priorities are engineering recommendations, not new sprint commitments or authority
to alter public behavior. P0 = release/safety blocker; P1 = required initial product
work; P2 = approved executive/research product work whose detailed contracts remain
to be resolved. Existing verified infrastructure should be reused.

## Main content

### Traceable engineering gap register

Evidence abbreviations follow IMPLEMENTATION_STATUS.md; short analysis filenames
refer to backend/app/analysis. Status is scoped, not a claim of final production readiness.

| Gap ID | Requirement | Priority | Current status | Evidence | Missing implementation | Required tests | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G01 | Licensed cryptocurrency provider and historical access | P0 | BLOCKED BY EXTERNAL DEPENDENCY | providers.py development adapter; fixture-only API | Select reviewed adapter/ingestion only after commercial/display/redistribution/analytics rights and access | Contract/failure/provenance/no-silent-provider tests with permitted fixtures | EXT-DATA | Written allowed uses/access, coverage and limits recorded; real permitted acquisition verified; no fabricated live output |
| G02 | Real-feed quality and timeframes | P0 | IMPLEMENTED BUT NOT FULLY VERIFIED | freshness.py; test_providers.py; test_historical_acceptance.py | Provider coverage/cadence/closed-candle/benchmark validation and real degraded-input scenarios | Future/duplicate/missing/gap/stale/MTF/benchmark feed contract tests | G01 | Licensed sample provenance retained; rejected/partial feeds safely classified; independent as-of frames |
| G03 | Analytical methodology and remaining evidence independence | P0 | PARTIALLY IMPLEMENTED | legacy-methodology-review.md; deterministic.py; test_contextual_contributions.py | Review legacy structure/trend/zones/volume/pattern formulas; approve public behavior changes before edits | Reference values, prefix/no-repaint/regime/conflict/duplicate-method tests | Founder methodology approval; G01/G04 | No inherited contextual votes restored; each directional method justified; no independence claim based on labels |
| G04 | Empirical historical evaluation and confidence calibration | P0 | PARTIALLY IMPLEMENTED | backtesting.py; calibration.py returns evaluation_pending | Define evaluation objective/acceptance, independent development/OOS data, empirical fitter/evaluator and bounded simulation limitations | OOS leakage/reproducibility/cost/spot/invalid-risk regressions plus approved empirical evaluation | EXT-DATA; founder acceptance protocol | Dataset/version/assumptions/report auditable; no invented profitability threshold or probability claim |
| G05 | Risk/opportunity policy acceptance | P0 | PARTIALLY IMPLEMENTED | RiskEngine/OpportunityFilter/ValidationEngine; test_safety_acceptance.py | Resolve limited liquidity/volatility policy and full release safety matrix without weakening existing gates | Missing/invalid/tight/wide geometry, weak liquidity, unavailable volatility, validation/backtest exclusion | G03; approved policy | Every applicable edge case has service/API/backtest evidence; rejected risk never actionable |
| G06 | Real customer identity and sole-founder MFA | P0 | PARTIALLY IMPLEMENTED | security/identity.py; dependencies.py; 22 tests | Reviewed vendor; email credential flow; sessions/rotation/revocation/logout; recovery; founder enrollment and protected route wiring | Real adapter audience/signature/revocation/outage, MFA/CSRF/recovery/abuse/no-admin-self-grant E2E | EXT-AUTH; security/cost review | Email customer login works; exactly founder issuer+subject with MFA; recovery cannot bypass; no delegated admin |
| G07 | Arabic-first Saudi customer experience | P1 | NOT IMPLEMENTED | English demo in AnalysisPage.tsx; typed panel tests | Arabic terminology/i18n/RTL and approved disclosures/accessibility, retaining honest confidence/provenance | RTL/mobile/keyboard/screen-reader/localized decision/loading/error/provenance/contract tests | Approved copy; G01/G06/G17 | Arabic-first customer flow tested; no fixture portrayed as live and no promised returns |
| G08 | PostgreSQL and environment isolation | P0 | PARTIALLY IMPLEMENTED | SQLAlchemy/Alembic scaffolding; SQLite recovery tests; no PostgreSQL driver in requirements | Approved driver/configuration; disposable PostgreSQL migrations/transactions; distinct environments and recovery | Actual PostgreSQL upgrade/downgrade/rollback/concurrency/backup-restore checks | EXT-INFRA; intended PostgreSQL already approved | DB behavior and restore verified on PostgreSQL; no shared production/test credentials or data |
| G09 | Bounded AI explanation | P1 | BLOCKED BY EXTERNAL DEPENDENCY | AIReasoningLayer returns unavailable; ExplainabilityEngine final-decision summary | Provider-neutral reviewed adapter, validated explanation packet, Arabic narrative with safe fallback | No fabricated evidence/decision override, injection/data-minimization/outage/privacy tests | EXT-AI; customer-data transfer approval | Narrative references supplied validated evidence; unavailable path honest; no external data sharing before approval |
| G10 | Flexible subscription, unit economics and Saudi billing | P1 | REQUIRES FOUNDER DECISION | No billing runtime; pricing expressly deferred | Measure actual per-customer operating cost; approved flexible prices; payment/entitlement/webhook/accounting/refund/cancellation design | Idempotency/signature/replay/recurrence/refund/cancellation/VAT-invoice cases after review | EXT-PAY; EXT-REG; G06; actual costs | No fixed 169 SAR assumption; founder price approval; processor capabilities and approved policies verified |
| G11 | Eleven-section founder Command Center | P1 | NOT IMPLEMENTED | No administration UI; telemetry hooks only | Exactly approved eleven sections, founder-only APIs/UI, audited sensitive decisions; no delegated staff access | All section routes, unauthorized/customer/no-MFA denial, scope/approval/audit tests | G06/G15; permissions for individual actions | Eleven and only eleven top-level sections; AI CTO/CFO nested as approved; no privilege bypass |
| G12 | AI CEO/CTO/CFO advisory systems | P2 | NOT IMPLEMENTED | Approved placement only; no runtime code | Define inputs/outputs, data access, cost limits and low-risk automation permissions; founder approval for sensitive actions | No unauthorized execution/data transfer, grounded summaries, approval/audit failure tests | G11/G09; founder action-policy decisions | CEO Brief top-level, CTO in Engineering, CFO in Finance; no inferred autonomous financial/product authority |
| G13 | Independent Board Meeting | P2 | NOT IMPLEMENTED | Approved section 11; no model/UI/service | Weekly founder-interactive text meetings, agenda/participants/minutes/decisions/follow-up persistence and approval workflow | Founder-only access, auditability, meeting/decision/action consistency and recovery | G06/G11/G12; meeting contract decisions | Independent eleventh section works; interaction restricted to founder executive context, not customer AI chat |
| G14 | Research Lab and Evolution Center | P2 | NOT IMPLEMENTED | No runtime product; offline calibration is distinct | Define reviewed research/evolution proposals and traceability; no automatic production strategy deployment | Sandbox/isolation/approval/version/reproducibility/data-rights regression tests | G04/G11; founder evolution permissions | Proposals tied to evidence and explicit approval; no unapproved model/engine/strategy promotion |
| G15 | Durable observability, incidents and audit | P1 | PARTIALLY IMPLEMENTED | telemetry.py; safe logs; request-isolation tests | Export/retention/access/actor correlation/incident runbooks and approved low-risk monitoring | Sink outage, redaction, durability/retention/access and alert/incident drills | EXT-OPS; G06/G11 | Intelligence Health analytical health distinct from Mission Control operational health; no financial metrics invented |
| G16 | Production security acceptance | P0 | PARTIALLY IMPLEMENTED | Boundary tests, sanitized API errors, non-root CI container | Threat model, dependency/security review, rate/abuse controls, secure sessions, durable sensitive-operation audit | Approved penetration/abuse/auth/session/secrets/dependency checks on release artifact | G06/G08; security review | No bypass/raw secrets/unsafe provider calls; findings remediated or formally accepted before release |
| G17 | Saudi regulatory/privacy/commercial review | P0 | REQUIRES FOUNDER DECISION | No legal/regulatory acceptance evidence | Qualified review of intended analysis/disclosures, data protection/consent/retention, commerce/tax/invoicing obligations | Approved disclosure/privacy/consent/retention/account-deletion/invoice acceptance cases as applicable | EXT-REG; EXT-PAY; founder/legal specialists | Applicable requirements established by qualified review; no unsupported legal compliance claims |
| G18 | Production deployment and recoverability | P0 | BLOCKED BY EXTERNAL DEPENDENCY | Docker/CI/SQLite smoke succeeds, no deployment proof | Hosting/database/domain/access/secret management; approved monitoring/backups/RPO/RTO; deployment and restore drills | Real release smoke, access/TLS/rollback/restore and realistic sustained load tests | EXT-INFRA/EXT-OPS; G08/G16/G17; founder release approval | Target environment verified with recovery objectives met; commercial deployment explicitly approved |
| G19 | Enforce approved on-demand/no-execution boundaries | P1 | IMPLEMENTED BUT NOT FULLY VERIFIED | Request-driven demo; no scanner/trading/customer-chat modules found | Preserve on-demand only; approved requirements in future routes/jobs/UX; distinguish internal executive monitoring | Negative tests for proactive customer scanning/opportunity alerts/execution/chat; explicit submit behavior | FOUNDER_DECISIONS.md | No autonomous customer opportunities/alerts/trades or customer interactive AI chat introduced |
| G20 | Historical specification conflicts and evidence maintenance | P1 | PARTIALLY IMPLEMENTED | Older proposed docs; requirement matrix; handover conflict register | Next Goal reconcile active planning with explicit newer approvals; preserve historical versions and avoid rebuilds | Link/path/traceability checks, requirement-ID coverage and approval-source review | Handover package and founder decisions | Every feature has status/test/gap/approval source; old proposals never override latest decisions |

### External dependency and approval register

| ID | Category / unresolved items | Current status | Required evidence / next owner action | Related gaps |
| --- | --- | --- | --- | --- |
| EXT-DATA | Provider selection; historical access; commercial analytics, display/redistribution restrictions; quality, coverage, cadence, rate limits and allowed evaluation uses | BLOCKED BY EXTERNAL DEPENDENCY | Founder/vendor establish written rights, approved datasets/uses and secure access; do not post secrets or assume public API availability grants rights | G01-G04 |
| EXT-AI | Provider/model; privacy/data minimization; customer-data transfer permission; measured cost; reliability/fallback constraints | REQUIRES FOUNDER DECISION | Reviewed comparison without purchase, privacy/security approval, versioned contract and tested safe fallback; no customer transfer until approved | G09/G12/G13 |
| EXT-AUTH | Identity vendor; credential flow; MFA factors/enrollment/freshness; sessions, recovery and founder identity binding | REQUIRES FOUNDER DECISION | Security/cost review and reviewed lifecycle; roles already resolved (customers plus one founder, no employee delegation) | G06/G11 |
| EXT-PAY | Saudi processor; Mada/Apple Pay/Visa/Mastercard support; recurring billing; VAT/invoicing; refunds/cancellation | REQUIRES FOUNDER DECISION | Establish actual processor capabilities/contract, qualified invoicing/tax requirements and founder-approved policies; no paid commitment; price after real unit costs | G10/G17 |
| EXT-INFRA | Hosting, database hosting, isolated environments, domain, deployment approval, operator access, backup destination/retention/RPO/RTO | BLOCKED BY EXTERNAL DEPENDENCY | PostgreSQL intent already approved; founder/security select environment and approve provisioning/release; prove migration/restore on that target | G08/G18 |
| EXT-OPS | Monitoring/export/alerting destinations, audit actor correlation/retention/access, incident ownership and escalation | REQUIRES FOUNDER DECISION | Define permitted low-risk reporting, provider/retention/security controls, analytical-vs-operational health contracts and incident drills | G11/G15/G18 |
| EXT-REG | Saudi financial-service regulatory review; disclosures; privacy/data protection; commercial/tax obligations | REQUIRES FOUNDER DECISION | Qualified legal/privacy/tax review of intended product and data flows; documented applicable controls/acceptance; no unsupported legal-compliance conclusion | G10/G17/G18 |

### Safe continuation order

G20 also includes the absent root .editorconfig: historical Sprint 1A.1 revisions
are preserved in the recovery pack, but this file is not on the current feature
branch. Reconcile this repository-quality requirement without rebuilding or
silently claiming it was already delivered in the active tree.

1. Reinspect received HEAD and handover evidence; reconcile scope/approval conflicts.
2. Resolve providers/rights and identity review in parallel with detailed contract
   work that needs no paid service or customer-data transfer.
3. Complete reviewed legacy methodologies/risk policy and independent empirical
   evaluation; preserve safety tests and Option A.
4. Integrate reviewed customer identity, PostgreSQL, licensed data and Arabic UX;
   prove actual end-to-end behavior before lifting any production restriction.
5. Implement approved billing/Command Center/executive/research scope according
   to resolved contracts and founder approval gates, not inferred permissions.
6. Complete privacy/regulatory/security/operations/recovery and release acceptance.

This is a dependency ordering for the next Goal, not implementation during handover.
Unresolved external decisions do not authorize silently removing their requirements.

## Related documents

- [Implementation status](IMPLEMENTATION_STATUS.md)
- [Founder decisions](FOUNDER_DECISIONS.md)
- [New Goal instructions](NEW_GOAL_START_HERE.md)
- [Acceptance dependencies](../03-engineering/acceptance-dependencies.md)

## Change history

- 2.0.0 — Added current handover overlay; original source/status evidence preserved.

- 1.0.0 — Established 20 engineering gaps and seven external-dependency categories.
