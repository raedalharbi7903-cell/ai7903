# Dependency-aware implementation plan

Version: 1.0 | Updated: 2026-10-29 | Status: executing

| Package | Required changes and files | Acceptance and tests | Depends on | Evidence |
| --- | --- | --- | --- | --- |
| P0 memory | Root governance/inventory/progress files | Source-grounded scope, no invented approvals | Repository inspection | Established; historical documents recovered unchanged |
| P1 advanced analysis | analysis/advanced.py, deterministic.py, engines.py; dedicated tests | Effective validated configs; four divergence classes; closed confirmed matched pivots; stable references; sweep/volume/candle boundaries | P0 | Implemented/tested on synthetic fixtures; empirical acceptance pending |
| P2 safety integration | engines.py, providers.py, pipeline.py, risk tests | Family conflicts cannot inflate votes; invalid data/risk never actionable; final explanation agrees with final decision | P1 | Partial: same-family/geometry/error gates verified; cross-family contribution change requires CTO decision |
| P3 historical evaluation | backtesting.py, calibration.py, historical tests | True as-of frames, fees/slippage, no lookahead, invalid-trade exclusion, reproducible metrics and OOS isolation | P2 | Synthetic service regressions verified; approved historical datasets/calibration protocol pending |
| P4 API/frontend | api/v1/analysis.py, frontend/src, frontend tooling/tests | Strict fixture provenance; typed panels, five states, safe errors, loading/empty/degraded states, actual API integration tests | P2 | Fixture experience and real HTTP integration verified; commercial/live/auth scope not complete |
| P5 operational/security scope | docs/06-security, docs/07-organization, docs/09-devops and corresponding runtime modules | Implement reconstructable approved scope; leave unknown roles/providers explicitly unresolved; deployment and restore evidence | P0, P4; external decisions | CI, container, migrations, disposable recovery, bounded concurrency verified; production target/access/backup decisions pending |
| P6 acceptance | Backend/frontend checks and relevant documentation | Full tests, static checks, formatting, builds, leakage/security review; feature branch clean and pushed | P1-P5 | 17 local gates pass; hosted latest run pending; product acceptance not established |

After each substantial package, record exact commands and outcomes in PROGRESS.md,
commit coherent progress, then continue independent executable work. No arbitrary
single-file checkpoint counts as completion.

## Current evidence overlay

### Active full-platform work packages — 2026-10-30

Preserve the handover as immutable historical evidence; do not reconstruct it.
The 31-section master directive and canonical registry retain the complete scope.

1. A1: reconcile requirements and explicit design/commercial/environment changes;
   maintain code/test reverse references and source-integrity tooling.
2. C1: provider-neutral acquisition into existing AnalysisService: strict snapshots,
   bounded retry, provenance/coverage/freshness and isolated optional caching.
   Real licensed retrieval remains blocked, not complete.
3. D1: centralized provisional design tokens and visible pending approval; no
   final palette, font, theme or layout acceptance. Continue functional work.
4. C2 next: PostgreSQL driver and actual disposable PostgreSQL CI acceptance;
   no production resource or deployment. Then customer-data isolation/persistence,
   provider-neutral subscription lifecycle and approved functional workflows.
5. Continue B-G from the master directive with G01-G20 retained. Methodology
   changes need approved specificity; vendors, privacy, pricing and visuals
   remain explicitly gated. A1/C1/D1 are checkpoints, never platform completion.

C2 implementation now adds pinned Psycopg, four environment names, staging demo
denial and an owned, loopback-only, digest-pinned PostgreSQL harness. Focused local
configuration/migration/API checks pass; actual server and restore acceptance
requires the new hosted step. No production database or business tables provisioned.

C2 runtime is now VERIFIED for disposable CI: run 41058711415 at 12e22e1 passed
six actual PG tests, pg_dump/restore and all ordinary gates/container checks.
D2 adds Arabic/RTL functional analysis, safe client errors and pending visual
approval. Next C3: owner-scoped history persistence/retention gates using existing
service/repository/database boundaries, with cross-account tests and PG migration
verification. No real customer data, identity vendor, paid calls or production deploy.

2026-10-30 access-policy update: founder approved email-based customers and one
founder-only MFA administrator, no delegated/employee roles. Provider-neutral
identity contracts and fail-closed FastAPI dependencies are implemented/tested
without exposing new public routes. Next identity package requires reviewed
vendor selection and actual enrollment/session/recovery integration.
PostgreSQL production intent and environment separation are approved; runtime
PostgreSQL/deployment acceptance is not established. External AI customer-data
transfer and paid commitments remain prohibited without further approval.

CTO Option A approved on 2026-10-29 and implemented: contextual/level-zone/basic
liquidity observations no longer contribute inherited direction to confluence or
confidence. Production-service, API serialization, contextual-only and retained
sweep-method regressions cover this change. The earlier P2 approval dependency is
resolved for this bounded correction; broader empirical method validation remains.

P0 is established. P1-P4 have verified integrated implementation at 7494cf8, with
remaining methodological limits listed in the requirement-evidence matrix.
P5 includes non-root container/healthcheck, reproducible verification runner,
runner failure tests and operational runbook. Local Docker is unavailable, but
hosted Docker execution is verified. P6 local gates pass, but full product acceptance remains
incomplete. Next: hosted CI configuration/execution and documentation consistency
audit, followed by remaining independent security/performance work. External
provider/identity/role decisions remain unresolved, not silently deferred.

Hosted CI execution is now verified: run 40917970124 at b8d8499 PASSED all local
equivalent gates, Docker build and container runtime safety. Continue with broad
security/concurrency acceptance, restore/deployment evidence where executable,
remaining engine-methodology review and full semantic documentation reconciliation.
