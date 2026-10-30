---
title: B1 Grounded Arabic Explanation Delivery
document_id: DOC-DELIVERY-B1-001
version: 1.0.1
status: verified-local-and-hosted-fallback
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-AR-EXPLANATION-001]
---

# B1 delivery

## Hosted publication receipt

Source d68a93f73790cdab9d1899298b74f633638870ae, hosted run 41069838855/job
124110728138 SUCCESS: all 17 gates, eight actual PostgreSQL tests, dump/restore,
container build/runtime and actual frontend/API rendering PASS. See
[retained evidence](../10-testing/arabic-explanation-acceptance-evidence.json).
This supersedes precommit pending entries below, not full AI/product acceptance.
Direct application import initially failed without required environment settings;
repeated with explicit synthetic testing configuration PASS. Compile/pip PASS.
Git LF-to-CRLF notices reflect existing checkout settings; no renormalization,
discarded work or hidden test warning. No changes to main.

## 1. Executive summary

IMPLEMENTATION IN PROGRESS. Grounded Arabic deterministic explanation now reaches
customers through the existing pipeline/API/frontend. It agrees with final safety
state, labels fixtures/uncalibrated limitations, cites actual evidence and excludes
untrusted source prose. Not an external AI model, rich AI narrative, final visual
design or full platform completion.

## 2. Architecture decisions

Green: fixed safe fallback sentences, typed structured references, no context
mutation, late-failure reconciliation and stale-client-payload guards.
Yellow: additive optional data.arabic_explanation in the existing free-form engine
data contract, with its own deterministic-ar-v1 methodology version. Legacy summary,
top-level API 1.0 and request shape unchanged; older responses remain supported.
No new route, library, engine slot, second pipeline, decision/risk/confluence formula,
provider or transfer of customer data. This implements approved Arabic/fallback scope.
Trade-off: fixed prose cannot explain every detailed reason yet; no external
prompt-injection, provider cost/reliability or full narrative-quality certification.

## 3. Repository tree

Complete current tracked/nonignored source tree below, no collapsed directories.
Dependencies/build/cache/Git internals excluded; historical recovery files preserved.

## 4. File changes

Added:
- backend/app/analysis/explanations.py
- backend/tests/analysis/test_arabic_explanation.py
- docs/05-analysis/arabic-deterministic-explanation.md
- frontend/src/types/explanation.test.ts
- frontend/src/types/explanation.ts
- docs/delivery/b1-arabic-explanation-delivery.md

Modified:
- IMPLEMENTATION_PLAN.md
- PROGRESS.md
- PROJECT_SPEC.md
- backend/app/analysis/engines.py
- backend/app/analysis/pipeline.py
- docs/02-product/canonical-requirements.json
- docs/04-architecture/explainability-architecture.md
- docs/10-testing/requirement-evidence-matrix.md
- docs/README.md
- frontend/src/features/analysis/AnalysisResults.test.tsx
- frontend/src/features/analysis/AnalysisResults.tsx
- frontend/src/features/analysis/analysis.integration.test.tsx
- frontend/src/i18n/ar.ts

Deleted: none. Renamed: none.

## 5. Git report

Branch feature/crypto-analysis-validation.
Baseline fa523cd (published C3 evidence); implementation source C3 638e3f8
hosted run 41068207446 passed full stack, eight actual PG tests and container.
Commit message: feat: add grounded Arabic deterministic explanations.
New hash/push/CI state must be recorded from real publication, not guessed here.
No merge, main push or force-push. No new PR required by this scoped package.

## 6. Validation report

| Check | Actual result |
| --- | --- |
| Backend full Pytest | PASS — 443, 17.63s |
| Arabic focused + failure isolation | PASS — 19 before final full regression |
| Backend Ruff | PASS |
| Backend Black | PASS — 93 files unchanged |
| Frontend tests | PASS — 33, six files, 5.99s |
| TypeScript | PASS — pnpm typecheck |
| ESLint | PASS — pnpm lint |
| Prettier | PASS — pnpm format:check |
| Frontend build | PASS — pnpm build, 279ms; JS 274.15 kB/gzip 87.47 kB |
| Tooling | PASS — 24, 0.125s |
| Documentation links | Rechecked after report creation |
| Real React/HTTP/FastAPI/pipeline integration | PASS — no analytical responses mocked |
| Backend import/compile/pip, frozen frontend deps/peers | Prior full checkpoint PASS; unchanged dependency manifests, not independently rerun locally for B1 |
| Actual local Docker/PostgreSQL | NOT VERIFIED — Docker unavailable locally |
| B1 source-specific hosted full/PG/container | PENDING commit/push and observed run |
| Backend separate mypy/Pyright | NOT CONFIGURED, no false type-check claim |
| External AI / live licensed data / visual/browser production acceptance | NOT VERIFIED |

Commands from backend: python -m pytest -o cache_dir=../.verification/pytest-cache
--tb=short; python -m ruff check . alembic/env.py; python -m black --check app tests
integration alembic/env.py. Tooling: unittest discover -s scripts -p test_*.py.
Initial two Ruff overlength Arabic literals repaired by splitting literals.
No failing assertion removed or warning suppressed.

## 7. Definition of done

- Completed: actual existing service returns matching Arabic for all five states.
- Completed: late engine failures reconcile Arabic and legacy summaries.
- Completed: actual evidence references and explicit conflicts, no new votes.
- Completed: no interpolation of malicious free-form source instructions/prose.
- Completed: typed compatible client guard and withheld stale/malformed narrative.
- Completed: actual API-to-React rendering with synthetic/deterministic labels.
- Completed: affected local quality gates and evidence documentation.
- Pending: B1 source-specific hosted verification.
- Not completed: rich reason translation/reference UI, generative provider/privacy/
  cost/security acceptance, final copy/visual/browser and production approval.
AN-C22 remains PARTIALLY IMPLEMENTED; AIReasoningLayer remains unavailable.

## 8. Known issues

No approved external AI provider/privacy agreement. No customer chat or external
network call added. Arabic fallback is static and not a fully reviewed narrative.
References are structured but not yet a dedicated rich evidence-drilldown UI.
Some existing analytical findings/warnings remain original English.

## 9. Breaking changes

No breaking public API changes. Optional nested object extends existing engine
data; legacy summary and older response rendering retained. No migration in B1.
Invalid/stale new narrative is withheld; no analytical outcome changed.

## 10. Performance and security

Linear rendering over existing evidence, no external cost/network, no fabricated
performance metric. Small production bundle increase reported above, not a speed
benchmark. Raw source finding/provider strings excluded from fixed prose; React
renders text, never HTML. No numerical confidence or invented market price.
No future external-model security guarantee inferred from a template test.

## 11. CTO recommendations

Keep deterministic safety reconciliation authoritative for future narratives.
Use reviewed reason codes and references for richer explanation, then review
Arabic wording/accessibility and founder design. Do not activate external AI
until provider/privacy/cost approval and real failure/claim tests exist.

## 12. Questions for CTO

No new routine decision required. Existing privacy/provider and final
copy/design/production approvals remain unresolved and are not inferred.

## 13. Next sprint readiness

Continue the existing goal, not another sprint or platform-completion claim.
Next: richer approved reason references, provider-neutral customer workflows and
retention/auth/public history integration once release requirements are resolved.
Independent internal work remains; green tests are not commercial launch approval.

## Complete repository tree

```text
ai-trading-platform/
├── .editorconfig
├── .env.example
├── .github
│   ├── .gitkeep
│   └── workflows
│       └── quality.yml
├── .gitignore
├── AGENTS.md
├── IMPLEMENTATION_PLAN.md
├── LICENSE
├── Makefile
├── PROGRESS.md
├── PROJECT_SPEC.md
├── README.md
├── backend
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── alembic
│   │   ├── env.py
│   │   └── versions
│   │       ├── 20260725_0001_initial_schema.py
│   │       └── 20261030_0002_analysis_history.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── analysis
│   │   │   ├── __init__.py
│   │   │   ├── advanced.py
│   │   │   ├── backtesting.py
│   │   │   ├── calibration.py
│   │   │   ├── context.py
│   │   │   ├── contracts.py
│   │   │   ├── data_cache.py
│   │   │   ├── data_contracts.py
│   │   │   ├── deterministic.py
│   │   │   ├── engines.py
│   │   │   ├── explanations.py
│   │   │   ├── freshness.py
│   │   │   ├── models.py
│   │   │   ├── pipeline.py
│   │   │   ├── providers.py
│   │   │   ├── registry.py
│   │   │   ├── service.py
│   │   │   └── telemetry.py
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── router.py
│   │   │   └── v1
│   │   │       ├── __init__.py
│   │   │       ├── analysis.py
│   │   │       └── router.py
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── error_handlers.py
│   │   │   └── exceptions.py
│   │   ├── database
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── dependencies
│   │   │   ├── __init__.py
│   │   │   └── factories.py
│   │   ├── logging
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── analysis_history.py
│   │   │   └── mixins.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── analysis_history.py
│   │   │   └── base.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   └── health.py
│   │   ├── security
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   └── identity.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── analysis_history.py
│   │   │   ├── base.py
│   │   │   └── market_data.py
│   │   └── utils
│   │       └── __init__.py
│   ├── integration
│   │   └── test_postgres.py
│   ├── pyproject.toml
│   ├── requirements
│   │   ├── base.txt
│   │   └── dev.txt
│   └── tests
│       ├── analysis
│       │   ├── test_advanced_behavior.py
│       │   ├── test_advanced_pipeline.py
│       │   ├── test_advanced_structure.py
│       │   ├── test_arabic_explanation.py
│       │   ├── test_backtesting.py
│       │   ├── test_behavioral_matrix.py
│       │   ├── test_boolean_boundaries.py
│       │   ├── test_calibration.py
│       │   ├── test_contextual_contributions.py
│       │   ├── test_data_acquisition.py
│       │   ├── test_data_cache.py
│       │   ├── test_decision_states.py
│       │   ├── test_deterministic.py
│       │   ├── test_evidence_asof.py
│       │   ├── test_failure_isolation.py
│       │   ├── test_framework.py
│       │   ├── test_freshness_boundaries.py
│       │   ├── test_freshness_telemetry.py
│       │   ├── test_historical_acceptance.py
│       │   ├── test_integration_features.py
│       │   ├── test_numeric_boundaries.py
│       │   ├── test_pipeline.py
│       │   ├── test_providers.py
│       │   ├── test_request_isolation.py
│       │   └── test_safety_acceptance.py
│       ├── api
│       │   ├── test_analysis.py
│       │   ├── test_error_boundary.py
│       │   └── test_security_acceptance.py
│       ├── conftest.py
│       ├── security
│       │   └── test_identity_boundaries.py
│       ├── test_analysis_history.py
│       ├── test_database_session_lifecycle.py
│       ├── test_health.py
│       ├── test_migration_recovery.py
│       ├── test_postgres_configuration.py
│       └── test_repository_and_service.py
├── database
│   └── .gitkeep
├── docker
│   └── .gitkeep
├── docs
│   ├── .gitkeep
│   ├── 01-project
│   │   ├── ai-philosophy.md
│   │   ├── core-principles.md
│   │   ├── decision-hierarchy.md
│   │   ├── engineering-philosophy.md
│   │   ├── mission.md
│   │   ├── product-philosophy.md
│   │   ├── project-manifest.md
│   │   ├── success-metrics.md
│   │   └── vision.md
│   ├── 02-product
│   │   ├── analysis-output-experience.md
│   │   ├── approved-master-execution-goal.md
│   │   ├── canonical-requirements.json
│   │   ├── market-support.md
│   │   ├── mvp-definition.md
│   │   ├── out-of-scope.md
│   │   ├── personas.md
│   │   ├── product-boundaries.md
│   │   ├── product-experience.md
│   │   ├── product-requirements.md
│   │   ├── product-scope.md
│   │   ├── release-strategy.md
│   │   ├── roadmap.md
│   │   └── user-journeys.md
│   ├── 03-engineering
│   │   ├── acceptance-dependencies.md
│   │   ├── ai-coding-rules.md
│   │   ├── approval-policy.md
│   │   ├── arabic-functional-foundation.md
│   │   ├── branch-strategy.md
│   │   ├── ci-cd.md
│   │   ├── coding-standards.md
│   │   ├── definition-of-done.md
│   │   ├── dependency-management.md
│   │   ├── engineering-handbook.md
│   │   ├── environment-management.md
│   │   ├── founder-design-approval.md
│   │   ├── git-workflow.md
│   │   ├── observability-standards.md
│   │   ├── pull-request-policy.md
│   │   ├── technical-debt-policy.md
│   │   └── testing-standards.md
│   ├── 04-architecture
│   │   ├── ai-reasoning-architecture.md
│   │   ├── analysis-history-foundation.md
│   │   ├── analysis-intelligence-architecture.md
│   │   ├── analysis-pipeline.md
│   │   ├── api-architecture.md
│   │   ├── architecture-baseline.md
│   │   ├── backend-architecture.md
│   │   ├── confidence-architecture.md
│   │   ├── conflict-resolution.md
│   │   ├── data-architecture.md
│   │   ├── data-flow.md
│   │   ├── decision-architecture.md
│   │   ├── degraded-analysis-policy.md
│   │   ├── evidence-architecture.md
│   │   ├── explainability-architecture.md
│   │   ├── frontend-architecture.md
│   │   ├── multi-timeframe-architecture.md
│   │   ├── persistence-architecture.md
│   │   ├── repository-structure.md
│   │   ├── risk-architecture.md
│   │   ├── security-architecture.md
│   │   ├── system-overview.md
│   │   └── validation-architecture.md
│   ├── 05-analysis
│   │   ├── ai-layer.md
│   │   ├── analysis-output-standard.md
│   │   ├── analysis-philosophy.md
│   │   ├── arabic-deterministic-explanation.md
│   │   ├── backtesting-engine.md
│   │   ├── candlestick-engine.md
│   │   ├── confidence-engine.md
│   │   ├── confluence-engine.md
│   │   ├── correlation-engine.md
│   │   ├── data-acquisition-foundation.md
│   │   ├── data-engine.md
│   │   ├── decision-engine.md
│   │   ├── engine-catalog.md
│   │   ├── engine-contract-standard.md
│   │   ├── engine-dependency-model.md
│   │   ├── engine-ordering.md
│   │   ├── evidence-engine.md
│   │   ├── explainability-engine.md
│   │   ├── legacy-methodology-review.md
│   │   ├── liquidity-engine.md
│   │   ├── market-context-engine.md
│   │   ├── market-structure-engine.md
│   │   ├── momentum-engine.md
│   │   ├── multi-timeframe-engine.md
│   │   ├── opportunity-filter.md
│   │   ├── pattern-recognition-engine.md
│   │   ├── risk-engine.md
│   │   ├── strategy-layer.md
│   │   ├── supply-demand-engine.md
│   │   ├── support-resistance-engine.md
│   │   ├── trend-engine.md
│   │   ├── validation-engine.md
│   │   ├── volatility-engine.md
│   │   └── volume-engine.md
│   ├── 06-security
│   │   ├── audit-logging.md
│   │   ├── authentication.md
│   │   ├── authorization.md
│   │   ├── data-protection.md
│   │   ├── identity-access-foundation.md
│   │   ├── incident-response.md
│   │   ├── privacy.md
│   │   ├── secrets-management.md
│   │   ├── secure-development.md
│   │   ├── security-baseline.md
│   │   ├── security-boundaries.md
│   │   └── threat-model.md
│   ├── 07-organization
│   │   ├── administrative-roles.md
│   │   ├── approval-matrix.md
│   │   ├── decision-authority.md
│   │   ├── engineering-responsibilities.md
│   │   ├── operations-responsibilities.md
│   │   ├── organization-model.md
│   │   ├── product-responsibilities.md
│   │   └── roles-and-responsibilities.md
│   ├── 08-api
│   │   ├── api-standards.md
│   │   ├── authentication-contract.md
│   │   ├── error-contract.md
│   │   ├── external-api-integration.md
│   │   ├── filtering.md
│   │   ├── pagination.md
│   │   ├── rate-limiting.md
│   │   ├── response-contracts.md
│   │   ├── versioning.md
│   │   └── websocket-standards.md
│   ├── 09-devops
│   │   ├── backups.md
│   │   ├── ci-cd.md
│   │   ├── configuration.md
│   │   ├── deployment.md
│   │   ├── disaster-recovery.md
│   │   ├── docker.md
│   │   ├── environments.md
│   │   ├── local-development.md
│   │   ├── logging.md
│   │   ├── monitoring.md
│   │   ├── postgresql-acceptance.md
│   │   ├── release-process.md
│   │   ├── rollback.md
│   │   └── verification-runbook.md
│   ├── 10-testing
│   │   ├── ai-evaluation.md
│   │   ├── analysis-engine-testing.md
│   │   ├── api-testing.md
│   │   ├── backtesting.md
│   │   ├── contract-testing.md
│   │   ├── end-to-end-testing.md
│   │   ├── frontend-testing.md
│   │   ├── arabic-explanation-acceptance-evidence.json
│   │   ├── history-postgresql-acceptance-evidence.json
│   │   ├── integration-testing.md
│   │   ├── performance-testing.md
│   │   ├── postgresql-acceptance-evidence.json
│   │   ├── quality-gates.md
│   │   ├── regression-testing.md
│   │   ├── request-isolation-acceptance.md
│   │   ├── requirement-evidence-matrix.md
│   │   ├── runtime-resilience-results.md
│   │   ├── security-testing.md
│   │   ├── testing-strategy.md
│   │   └── unit-testing.md
│   ├── 11-adr
│   │   └── README.md
│   ├── README.md
│   ├── analysis-engine-architecture.md
│   ├── delivery
│   │   ├── a1-c1-d1-engineering-delivery.md
│   │   ├── b1-arabic-explanation-delivery.md
│   │   ├── c2-postgresql-engineering-delivery.md
│   │   ├── c3-history-engineering-delivery.md
│   │   ├── d2-arabic-engineering-delivery.md
│   │   ├── data-boundary-repair.md
│   │   ├── identity-foundation-engineering-delivery.md
│   │   └── option-a-engineering-delivery.md
│   └── handover
│       ├── FOUNDER_DECISIONS.md
│       ├── GOAL_TRANSITION_CHECKLIST.md
│       ├── IMPLEMENTATION_STATUS.md
│       ├── NEW_GOAL_START_HERE.md
│       ├── PROJECT_HANDOVER.md
│       ├── PUBLICATION_RECEIPT.md
│       ├── REMAINING_WORK.md
│       └── evidence
│           ├── README.md
│           ├── documentation-audit.json
│           ├── handover-validation.json
│           ├── hosted-preservation-ci.json
│           ├── latency-baseline.json
│           ├── preservation-review.json
│           ├── quality-gates.json
│           ├── recovery-object-inventory.json
│           ├── recovery-objects-5adf3bd68ef8bb13ff6650231da70dae89fc1165.idx
│           ├── recovery-objects-5adf3bd68ef8bb13ff6650231da70dae89fc1165.pack
│           └── recovery-objects-5adf3bd68ef8bb13ff6650231da70dae89fc1165.rev
├── frontend
│   ├── .env.example
│   ├── .gitkeep
│   ├── .prettierignore
│   ├── .prettierrc.json
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── src
│   │   ├── app
│   │   │   └── App.tsx
│   │   ├── components
│   │   │   └── Panel.tsx
│   │   ├── design
│   │   │   ├── approval.ts
│   │   │   └── tokens.test.ts
│   │   ├── features
│   │   │   └── analysis
│   │   │       ├── AnalysisResults.test.tsx
│   │   │       ├── AnalysisResults.tsx
│   │   │       ├── analysis.integration.test.tsx
│   │   │       └── fixture.ts
│   │   ├── i18n
│   │   │   ├── ar.test.ts
│   │   │   └── ar.ts
│   │   ├── layouts
│   │   │   └── Layout.tsx
│   │   ├── main.tsx
│   │   ├── pages
│   │   │   ├── AnalysisPage.test.tsx
│   │   │   ├── AnalysisPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── services
│   │   │   └── analysis.ts
│   │   ├── styles.css
│   │   ├── styles
│   │   │   └── tokens.css
│   │   ├── test
│   │   │   ├── results.ts
│   │   │   └── setup.ts
│   │   ├── types
│   │   │   ├── analysis.ts
│   │   │   ├── explanation.test.ts
│   │   │   └── explanation.ts
│   │   └── vite-env.d.ts
│   ├── tests
│   │   ├── api-setup.ts
│   │   └── diagnose-startup.mjs
│   ├── tsconfig.json
│   └── vite.config.ts
└── scripts
    ├── .gitkeep
    ├── audit_documents.py
    ├── benchmark_analysis.py
    ├── postgres_acceptance.py
    ├── smoke_container.py
    ├── test_audit_documents.py
    ├── test_design_tokens.py
    ├── test_postgres_acceptance.py
    ├── test_requirements.py
    ├── test_smoke_container.py
    ├── test_verify.py
    └── verify.py
```

