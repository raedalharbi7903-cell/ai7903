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
| Independent directional contributions | Several families reuse whole-prefix close direction; legacy review documents this | Approve conservative non-directional context/levels/liquidity contributions, or supply approved family-specific direction/dependency rules |
| Live and historical market data | Fixture endpoint does not acquire live data; commercial rights unestablished | Approved provider/dataset, permitted use and redistribution/commercial rights, access configuration through secure environment storage |
| AI explanation | Deterministic fallback works; no configured/approved AI integration | Provider/model and data-sharing/privacy constraints; no authorization to override deterministic safety |
| Authentication and administration | Production demo disabled; roles/permissions explicitly unrecoverable in existing docs | Identity method/provider, principal/role-permission model, approved administrative actions and access boundaries |
| Production deployment and recovery | CI container and disposable SQLite recovery pass | Deployment/database target, operator access, backup destination/retention, recovery objectives and approved operational environment |
| Empirical analytical acceptance | Synthetic and historical-prefix regressions pass, confidence uncalibrated | Approved independent datasets and evaluation/calibration acceptance protocol; no invented profitability thresholds |

### Directional contribution options

**A — Recommended immediate correction:** context/levels/liquidity observations
remain non-directional unless their own approved method establishes direction.
Pros: conservative, does not invent new market inference, removes unsupported
votes. Cons: changes fixture decisions/confidence and reduces actionable results.

**B — Explicit methodology first:** approve directional rules and dependencies per
family before implementation. Pros: richer analytical semantics and an auditable
design. Cons: additional design/calibration work and no immediate independence fix.

Neither option has been approved. Engineering must not silently implement either
as a routine cleanup because decision/confidence behavior changes are red-level.

### Acceptance evidence already obtained

Seventeen local gates cover backend/frontend behavior, contracts, lint/format,
build/import/dependencies and documentation file links. Hosted CI verified Linux
integration, container health/non-root/production denial and packaged migrations.
Disposable SQLite backup/restore and bounded service/API concurrency are verified.
These results do not provide the missing product decisions or production rights.

## Related documents

- [Project specification](../../PROJECT_SPEC.md)
- [Implementation plan](../../IMPLEMENTATION_PLAN.md)
- [Requirement evidence](../10-testing/requirement-evidence-matrix.md)
- [Legacy methodology review](../05-analysis/legacy-methodology-review.md)
- [Administrative roles](../07-organization/administrative-roles.md)

## Change history

- 1.0.0 — Consolidated unresolved approval/access dependencies after implementation audit.
