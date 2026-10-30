---
title: Product Acceptance Dependencies
document_id: DOC-ENG-ACCEPTANCE-DEPS-001
version: 1.0.0
status: decision-required
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-29
related_documents: [DOC-ANALYSIS-LEGACY-REVIEW-001]
---

# Product acceptance dependencies

## Purpose

Record remaining decisions that engineering cannot safely invent. This document
does not approve an implementation, shrink the project, or waive any requirement.

## Scope

Unresolved dependencies in PROJECT_SPEC.md and the current requirement matrix.
Generic continuation of the full goal is not approval of a specific red-level change.

## Main content

| Dependency | Current evidence | Required CTO direction or external evidence |
| --- | --- | --- |
| Independent directional contributions | CTO Option A implemented and verified; broader empirical independence unproven | Specific contribution approval resolved; independent datasets/method validation still required |
| Live and historical market data | Fixture endpoint does not acquire live data; commercial rights unestablished | Approved provider/dataset, permitted use and redistribution/commercial rights, access configuration through secure environment storage |
| AI explanation | Provider-neutral architecture approved; no vendor/model approved; customer data sharing prohibited pending approval | Vendor/model, privacy/data-sharing review; no paid commitments or deterministic-safety overrides |
| Authentication and administration | Email customers, single founder-only admin with MFA approved; neutral access dependencies implemented, not routed | Vendor security/cost review, enrollment, session/recovery integration and full runtime acceptance |
| Production deployment and recovery | PostgreSQL intended production DB and separate environments approved; CI/SQLite evidence only | Hosting vendor, PostgreSQL verification, operator access, backup/retention/RPO/RTO and founder release approval |
| Empirical analytical acceptance | Synthetic and historical-prefix regressions pass, confidence uncalibrated | Approved independent datasets and evaluation/calibration acceptance protocol; no invented profitability thresholds |

### Directional contribution options

**A — Recommended immediate correction:** context/levels/liquidity observations
remain non-directional unless their own approved method establishes direction.
Pros: conservative, does not invent new market inference, removes unsupported
votes. Cons: changes fixture decisions/confidence and reduces actionable results.

**B — Explicit methodology first:** approve directional rules and dependencies per
family before implementation. Pros: richer analytical semantics and an auditable
design. Cons: additional design/calibration work and no immediate independence fix.

On 2026-10-29 the CTO explicitly approved Option A through the approval question:
"keep context, levels and liquidity non-directional unless their own approved
method establishes direction." This authorizes removing inherited directional
votes from market context, support/resistance, supply/demand range/zone observations,
and basic liquidity. Sweep findings retain their separately implemented directional
method and existing liquidity family. It does not approve new weights, thresholds,
methodologies for other families, or calibrated confidence claims.

### Acceptance evidence already obtained

Seventeen local gates cover backend/frontend behavior, contracts, lint/format,
build/import/dependencies and documentation file links. Hosted CI verified Linux
integration, container health/non-root/production denial and packaged migrations.
Disposable SQLite backup/restore and bounded service/API concurrency are verified.
These results do not provide the missing product decisions or production rights.

### Subsequent founder approval

On 2026-10-30 the founder approved email customer identity, exactly one founder
administrator and mandatory MFA for exclusive Command Center access. No employee
or delegated roles are required. Authentication vendor remains pending security/
cost review. PostgreSQL and separate environments are approved intent; hosting
and actual deployment remain gated. No external AI customer-data transfer is
approved. See [identity foundation](../06-security/identity-access-foundation.md).
The market-data question received the same identity-policy answer, not data rights.

## Related documents

- [Project specification](../../PROJECT_SPEC.md)
- [Implementation plan](../../IMPLEMENTATION_PLAN.md)
- [Requirement evidence](../10-testing/requirement-evidence-matrix.md)
- [Legacy methodology review](../05-analysis/legacy-methodology-review.md)
- [Administrative roles](../07-organization/administrative-roles.md)

## Change history

- 1.0.0 — Consolidated unresolved approval/access dependencies after implementation audit.
