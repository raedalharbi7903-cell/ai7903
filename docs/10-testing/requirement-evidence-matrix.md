# Requirement-to-evidence matrix

Version 1.0 — 2026-10-29 — Engineering — incomplete product acceptance.

This matrix preserves every inventory row in PROJECT_SPEC.md. PASS applies only
to the stated tested behavior, not commercial readiness. The executable evidence
runner is scripts/verify.py; its local report is .verification/quality-gates.json.
No performance, calibration, provider-rights or deployment claims are inferred
from compilation or synthetic fixtures.

## Handover verification overlay — 2026-10-30

B1 source d68a93f7 hosted run 41069838855 SUCCESS: all 17 gates, eight actual
PostgreSQL tests/dump-restore and application container PASS. See
[retained evidence](arabic-explanation-acceptance-evidence.json). No AI vendor
or production/visual acceptance inferred.

B1 Arabic fallback: test_arabic_explanation.py covers all five actual service
decisions, late failures, source-text injection exclusion, conflict references
and state immutability. Frontend contract/UI and actual HTTP tests verify final
state matching and synthetic/deterministic labeling. 443 backend and 33 frontend
tests PASS locally. No external AI, privacy or final design acceptance inferred.

C3 source 638e3f8 hosted run 41068207446 completed SUCCESS: all full-stack gates,
eight actual PostgreSQL tests, history isolation/expiry, dump/restore and container
runtime. [Retained evidence](history-postgresql-acceptance-evidence.json).
This supersedes C3 hosted-pending wording below, not customer/production acceptance.

C3 CUSTOMER-16: internal history model/repository/service is tested with synthetic
trusted sessions, all 28 existing pipeline outputs, owner/issuer isolation,
equal-timestamp keysets, expired/unverified/mutated-session denial, finite/size
bounds, expiry purge and rollback. New migration head 20261030_0002 preserves the
initial revision. Two real PostgreSQL cases and restore row-count checks require
the C3 source-specific hosted run. No public history/customer feature completion.

Shared input boundary: backend/tests/analysis/test_boolean_boundaries.py has 20
cases rejecting boolean OHLCV and coerced closed/fixture flags, preserving valid
numbers and proving actual AnalysisService returns insufficient_data on malformed
raw input. Full checkpoint: 388 backend/30 frontend/23 tooling, all 17 gates PASS.
D2 hosted run 41064875772 succeeded at 272a057; later source needs its own CI.

Current execution scope is expanded and retained in the
[canonical register](../02-product/canonical-requirements.json), with grouped
requirements and code/test reverse references. The original rows below remain
historical evidence, not a substitute for the full 31-section directive.
New C1 tests cover provider-neutral acquisition/cache safety through AnalysisService;
D1 tests cover centralized provisional tokens and the pending-design notice.
These do not prove live ingestion, actual provider rights or founder visual approval.

DB-PG-ACCEPTANCE adds actual PostgreSQL tests outside the default SQLite test path,
run explicitly by scripts/postgres_acceptance.py in CI. Driver/configuration and
ownership-guard tests run locally; mocks do not establish server acceptance.
The canonical register records hosted runtime as pending until its own run succeeds.

That C2 run is now confirmed: 41058711415 at 12e22e1, six PostgreSQL tests PASS
(2.04s), real dump/restore and application container PASS. See
[retained evidence](postgresql-acceptance-evidence.json). This is not production.
D2 frontend verifies Arabic/RTL semantics, safe native/parse errors and actual API
integration (30 tests). Visual/font/viewport and complete Arabic narrative approval
remain open; no customer UI is marked visually VERIFIED COMPLETE.

The complete current inventory and expanded approved product requirements are in
[handover status](../handover/IMPLEMENTATION_STATUS.md), with missing work and
acceptance criteria in [G01-G20](../handover/REMAINING_WORK.md).
The founder approval/conflict register is
[FD01-FD19](../handover/FOUNDER_DECISIONS.md). Older rows/counts below remain
historical scoped records, not current completion claims.

Fresh authorized local verification at source a7f0b72 passed all 17 gates:
295 backend, 17 frontend and 11 tooling tests. Hosted run 41048839548 also passed
full-stack, Docker build and actual container safety/migration checks at that SHA.
Evidence is retained in docs/handover/evidence. Identity dependencies are default
deny and test-routed only; actual login/recovery/administration remains absent.
PostgreSQL intent is approved, runtime unverified. No empirical calibration,
licensed live data, Arabic-first production experience or commercial readiness
is inferred. The Option A correction is complete for its bounded scope; remaining
cross-method independence is not established.

| Requirement | Runtime location | Verification | Assessment |
| --- | --- | --- | --- |
| Backend foundation | backend/app/config, database, repositories, services | test_health.py; test_repository_and_service.py | PASS for tested foundation; real production DB deployment not verified |
| Registry, lifecycle, sequential service | backend/app/analysis/registry.py, pipeline.py, service.py | test_framework.py; test_pipeline.py | PASS for existing contracts |
| Legacy deterministic engines | deterministic.py, engines.py | test_deterministic.py; test_behavioral_matrix.py | PARTIAL: provisional methodologies need broader review |
| Four divergence classes and effective settings | advanced.py divergence | test_advanced_behavior.py | PASS synthetic classifications, matching, settings, prefix/confirmation behavior |
| Structure break timing | advanced.py market_transition | test_advanced_structure.py; test_advanced_behavior.py | PASS dedicated boundary and repeat-event tests |
| Liquidity inference | advanced.py liquidity_sweep | test_advanced_behavior.py | PASS directional/rejection/tolerance/conflict cases; not observed orders |
| Volume anomaly | advanced.py volume_anomaly | test_advanced_behavior.py | PASS configurable baseline, missing/invalid/zero and activity cases |
| Candle classifications | deterministic.py candlestick | test_behavioral_matrix.py; test_advanced_behavior.py | PARTIAL: geometry tested; contextual interpretation remains limited |
| Evidence and five decision states | engines.py | test_decision_states.py; test_safety_acceptance.py; legacy methodology review | PARTIAL: tested states/same-family grouping pass; different families reuse price-direction bias and independence is not established |
| Structural risk and validation | engines.py RiskEngine/ValidationEngine | test_safety_acceptance.py | PASS listed geometry/target/RR gates; volatility/liquidity policy still limited |
| MTF and correlation | engines.py | test_integration_features.py; test_historical_acceptance.py | PASS tested alignment/provenance/cadence and contextual correlation; broader regime validation remains |
| Historical evaluation | backtesting.py | test_backtesting.py; test_historical_acceptance.py | PASS tested as-of service execution, spot-only, gap stops, costs and reproducibility; not portfolio validation |
| OOS and calibration | calibration.py, backtesting.py | test_calibration.py; test_historical_acceptance.py | PARTIAL: split isolation tested; no empirical calibration |
| Typed fixture API | schemas/analysis.py, api/v1/analysis.py, models.py | tests/api/test_analysis.py | PASS fixture boundary and serialization; production demo disabled |
| Frontend foundation/tooling | frontend/src/app, layouts, vite.config.ts | typecheck; lint; format:check; build; peers check | PASS configured stack and quality gates |
| Analysis experience and API integration | frontend/src/features/analysis, services, pages | AnalysisResults.test.tsx; AnalysisPage.test.tsx; analysis.integration.test.tsx | PASS 15 tests including actual local FastAPI; full browser/accessibility certification absent |
| AI constrained narrative | engines.py AIReasoningLayer | test_pipeline.py unavailable-provider behavior | BLOCKED: no approved/configured provider; no narrative implementation |
| Live cryptocurrency data | providers.py | fixture-only API tests | BLOCKED: rights/access not established; no live integration acceptance |
| Authentication and administration | app/security; docs/06-security/identity-access-foundation.md | tests/security/test_identity_boundaries.py; production-demo denial | PARTIAL: approved founder/customer boundary tested; actual provider/session/recovery/routing integration absent |
| Operations and deployment | backend/Dockerfile; scripts/verify.py | hosted run 40917970124; container smoke; tooling tests | PARTIAL: Linux CI/build/runtime verified; deployment, restore and sustained load acceptance incomplete |
| Documentation/governance | docs; root project-memory files | historical blob checks; inline-file link audit; explicit inventory | PARTIAL: missing documents recovered unchanged; prose consistency and governance acceptance incomplete |
| Safety/licensing/Git constraints | API fixture boundary; feature branch | provenance tests; git status/remote checks | PASS tested boundaries; rights approval and commercial security acceptance not implied |

## Unresolved acceptance evidence

The CTO approved Option A identified in the
[legacy methodology review](../05-analysis/legacy-methodology-review.md).
Context, support/resistance, supply/demand zone and basic liquidity findings now
serialize null direction and do not add confluence/confidence votes. Their
measurements remain intact. Own-method liquidity sweeps retain direction but share
one liquidity family. Tests: test_contextual_contributions.py, including service,
API and contextual-only paths; frontend labels null/neutral findings as
non-directional observations. Remaining method independence/calibration is not
established merely by different family labels.

### Latest hosted/runtime evidence

Run 40917970124 at b8d8499 passed the complete Linux backend/frontend suite,
Docker build and container runtime smoke. The earlier frontend startup failure
below is historical: preserving the virtualenv interpreter path fixed it.
Current verified counts: 227 backend, 15 frontend and 11 tooling tests, 17 gates.

Request-isolation update: local gates now pass 236 backend, 16 frontend and
11 tooling tests. The service copies caller input into a request-owned snapshot;
mutation, 64-call service isolation, 32-call API isolation and 16 concurrent actual
HTTP client requests are covered. See [bounded acceptance](request-isolation-acceptance.md).
This extends regression evidence, not production security/capacity certification.

Migration/recovery extension: test_migration_recovery.py exercises actual Alembic
upgrade/current/downgrade, percent-containing URLs, offline SQL without a DB
connection, and SQLite backup/restore integrity using disposable test databases.
test_database_session_lifecycle.py covers cleanup/rollback/no hidden commits.
These do not prove production database recovery, scheduled backups, offsite
retention or approved RPO/RTO. Container packaging now includes migration sources;
the extended packaged-migration smoke requires its own hosted run evidence.
That evidence is now available: GitHub run 40919739638 at 7addc48 completed
successfully, including the packaged-migration smoke. Counts: 243 backend,
16 frontend, 11 tooling tests across 17 local/hosted gates.

Run 40915941075 verified container build, loopback health, non-root UID and
production-demo denial. Hosted full-stack verification remains FAIL on Linux
frontend startup; local Windows tests do not supersede this failure.
Historical evidence as-of semantics are additionally tested in
backend/tests/analysis/test_evidence_asof.py. Missing governance targets were
recovered unchanged; inline local file links now pass. Prose consistency,
deployment/restore and broader performance/security claims remain unverified.

Deployment target, identity provider, role permissions, commercial data rights and
AI provider remain explicit external decisions. Engineering work still includes
CI execution, load/security tests, legacy-engine review and cross-document audit.
The full specification is NOT COMPLETE. No row authorizes new product scope or
removes an agreed requirement.
