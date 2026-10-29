# Requirement-to-evidence matrix

Version 1.0 — 2026-10-29 — Engineering — incomplete product acceptance.

This matrix preserves every inventory row in PROJECT_SPEC.md. PASS applies only
to the stated tested behavior, not commercial readiness. The executable evidence
runner is scripts/verify.py; its local report is .verification/quality-gates.json.
No performance, calibration, provider-rights or deployment claims are inferred
from compilation or synthetic fixtures.

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
| Evidence and five decision states | engines.py | test_decision_states.py; test_safety_acceptance.py | PASS tested states and same-family contradictions |
| Structural risk and validation | engines.py RiskEngine/ValidationEngine | test_safety_acceptance.py | PASS listed geometry/target/RR gates; volatility/liquidity policy still limited |
| MTF and correlation | engines.py | test_integration_features.py; test_historical_acceptance.py | PASS tested alignment/provenance/cadence and contextual correlation; broader regime validation remains |
| Historical evaluation | backtesting.py | test_backtesting.py; test_historical_acceptance.py | PASS tested as-of service execution, spot-only, gap stops, costs and reproducibility; not portfolio validation |
| OOS and calibration | calibration.py, backtesting.py | test_calibration.py; test_historical_acceptance.py | PARTIAL: split isolation tested; no empirical calibration |
| Typed fixture API | schemas/analysis.py, api/v1/analysis.py, models.py | tests/api/test_analysis.py | PASS fixture boundary and serialization; production demo disabled |
| Frontend foundation/tooling | frontend/src/app, layouts, vite.config.ts | typecheck; lint; format:check; build; peers check | PASS configured stack and quality gates |
| Analysis experience and API integration | frontend/src/features/analysis, services, pages | AnalysisResults.test.tsx; AnalysisPage.test.tsx; analysis.integration.test.tsx | PASS 15 tests including actual local FastAPI; full browser/accessibility certification absent |
| AI constrained narrative | engines.py AIReasoningLayer | test_pipeline.py unavailable-provider behavior | BLOCKED: no approved/configured provider; no narrative implementation |
| Live cryptocurrency data | providers.py | fixture-only API tests | BLOCKED: rights/access not established; no live integration acceptance |
| Authentication and administration | docs/06-security, docs/07-organization | production-demo denial test only | BLOCKED/PARTIAL: role and identity decisions missing; no authentication implementation |
| Operations and deployment | backend/Dockerfile; scripts/verify.py | 4 verification-runner tests; full gate run | PARTIAL: non-root/healthcheck added; Docker build, hosted CI, deploy, restore and load tests not executed |
| Documentation/governance | docs; root project-memory files | source inspection and this explicit inventory | PARTIAL: missing governance targets and stale proposed documents remain |
| Safety/licensing/Git constraints | API fixture boundary; feature branch | provenance tests; git status/remote checks | PASS tested boundaries; rights approval and commercial security acceptance not implied |

## Unresolved acceptance evidence

### Latest hosted/runtime evidence

Run 40917970124 at b8d8499 passed the complete Linux backend/frontend suite,
Docker build and container runtime smoke. The earlier frontend startup failure
below is historical: preserving the virtualenv interpreter path fixed it.
Current verified counts: 227 backend, 15 frontend and 11 tooling tests, 17 gates.

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
