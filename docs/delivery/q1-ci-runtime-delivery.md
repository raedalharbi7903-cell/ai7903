---
title: Q1 CI Runtime Engineering Delivery
document_id: DOC-DELIVERY-Q1-001
version: 1.0.0
status: verified-local-policy-hosted-pending
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-CI-ACTIONS-001, DOC-DELIVERY-C5-001]
---

# Q1 delivery

## 1. Executive summary

IMPLEMENTATION IN PROGRESS. Addressed observed deprecated action Node20 targets
with reviewed immutable native Node24 actions from the same maintainers.
No application dependency, installed tool version, business behavior or API change.
C5 protected read application remains implemented/verified; platform is incomplete.
Separate Starlette/AnyIO deprecation is not suppressed or declared resolved.

## 2. Architecture decisions

Green CI maintenance / yellow internal execution-runtime refresh.
Reviewed official major-release notes, exact commit source action.yml and existing
input compatibility. New ESM action implementations remain internal to CI; no used
removed input or registry-token dependency. Full40hex pins and immutable source URLs.
Read-only token, no persisted checkout credential, branch/PR/manual triggers,
Python3.12/Node24.14.0/pnpm11.25.0 and all acceptance steps unchanged.
Explicit frontend package_json_file, caches false and artifact archive true keep
monorepo/archive semantics stable. No architecture/provider/product decision.
Trade-off: hosted execution must prove runtime compatibility, source tests cannot.

## 3. Repository tree

Complete tracked/nonignored source tree below; no collapsed source directories.
Ignored build/cache/dependencies/Git internals excluded. No source/history deleted.

## 4. File changes

Added:
- docs/09-devops/ci-action-baseline.json
- docs/09-devops/ci-action-policy.md
- scripts/test_ci_policy.py
- docs/delivery/q1-ci-runtime-delivery.md

Modified:
- .github/workflows/quality.yml
- IMPLEMENTATION_PLAN.md
- PROGRESS.md
- PROJECT_SPEC.md
- docs/02-product/canonical-requirements.json
- docs/10-testing/requirement-evidence-matrix.md
- docs/README.md

Deleted: none. Renamed: none.
No backend/frontend application source or requirements/lockfile changed.

## 5. Git report

Branch feature/crypto-analysis-validation, baseline
d284021af993a64589856ed6945e65650135b6ab.
Commit message: ci: refresh immutable Node 24 action runtimes.
Exact new SHA/push/CI must be observed after publication. No main/merge/force push.

## 6. Validation report

| Check | Actual outcome |
| --- | --- |
| Tooling unittest discovery | PASS — 28, 0.244s after immutable-source pin check |
| Tooling Ruff / Black | PASS |
| YAML parsing and scoped jobs/permissions | PASS — existing PyYAML BaseLoader |
| Immutable action source review | PASS — five exact SHA action.yml files use node24 |
| Used input compatibility review | PASS — official metadata and release notes |
| Documentation links | Rechecked after completing report |
| Backend/frontend local tests/build | NOT RERUN — no app/dependency change; C5 480/65 PASS |
| Hosted new workflow / PG / container | PENDING own-source run |
| Actual local Docker | NOT VERIFIED — unavailable locally |
| Runtime framework dependency upgrade | NOT PERFORMED, no warning suppression |
| Production/deployment/provider/privacy | NOT VERIFIED |

Four new source-policy tests assert pin allowlist/credentials/triggers/runtime/cache
and mandatory test/PG/container/evidence steps. They are not a YAML parser or remote
action acceptance. Local parser checks syntax; only actual hosted execution proves
action compatibility. C5 source e53a808 run41097056519 had nine PG tests PASS/one
Starlette-AnyIO deprecation (2.54s); that original warning remains transparently retained.
Standalone pip show emitted Windows terminal Unicode logging errors; UTF-8 metadata
query succeeded, no package/app bug or failing test was disguised.

## 7. Definition of done

- Completed: review exact official maintained release/runtime/input compatibility.
- Completed: immutable Node24 action pins, no mutable tag or authority expansion.
- Completed: preserve app tools/deps, credentials, triggers and complete acceptance.
- Completed: add source-policy regressions and parse workflow locally.
- Pending: hosted new action source actually executes full stack/PG/container.
- Not completed: separate framework deprecation review or full platform/production.
No guarantee of zero remaining warnings before own-source logs are inspected.

## 8. Known issues

Existing FastAPI0.116.1/Starlette0.47.3 TestClient/AnyIO deprecated alias remains.
Do not downgrade/filter/patch site packages to hide it. Review a compatible
maintained runtime update separately; major behavior/dependency changes need
required approval. Runtime image is non-root despite build-time pip warning.
No fully reproducible transitive backend lock/security audit is claimed here.

## 9. Breaking changes

No application/public API breaking changes. CI action majors updated with reviewed
used inputs preserved; hosted validation remains mandatory. No dependency replacement,
customer data, production resource or deployment.

## 10. Performance and security

No customer-data flow, paid resource or deployment permission added. Caches disabled,
artifact retention14 unchanged, all source pins40hex reviewed. No speed/cost or
supply-chain attestation claim; immutable pins do not replace full security review.
No new secrets/registry authentication/OIDC/write token granted.

## 11. CTO recommendations

Keep immutable-source and permission guards. Observe actual new runtime logs and
retain any warnings/failures. Separately address compatible runtime dependencies
and deterministic security/locking checks without altering API semantics.

## 12. Questions for CTO

No new product/vendor/paid decision for this CI-only maintenance. Major application
dependency replacement was not approved or performed; no final production claim.
Existing identity/privacy/data/visual/commercial decisions remain unresolved.

## 13. Next sprint readiness

Continue existing full-platform goal, not another sprint or completion declaration.
Observe this CI run, then resume consented atomic audit/history mutation/CSRF and
remaining approved customer/commercial/Command Center work.

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
│   │   │       ├── history.py
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
│   │   │   ├── factories.py
│   │   │   └── history.py
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
│   │   │   ├── health.py
│   │   │   └── history.py
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
│       │   ├── test_provider_denial.py
│       │   ├── test_providers.py
│       │   ├── test_request_isolation.py
│       │   └── test_safety_acceptance.py
│       ├── api
│       │   ├── test_analysis.py
│       │   ├── test_error_boundary.py
│       │   ├── test_history.py
│       │   └── test_security_acceptance.py
│       ├── conftest.py
│       ├── http_history_fixture.py
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
│   │   ├── history-api.md
│   │   ├── pagination.md
│   │   ├── rate-limiting.md
│   │   ├── response-contracts.md
│   │   ├── versioning.md
│   │   └── websocket-standards.md
│   ├── 09-devops
│   │   ├── backups.md
│   │   ├── ci-action-baseline.json
│   │   ├── ci-action-policy.md
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
│   │   ├── arabic-explanation-acceptance-evidence.json
│   │   ├── backtesting.md
│   │   ├── contract-testing.md
│   │   ├── end-to-end-testing.md
│   │   ├── frontend-testing.md
│   │   ├── history-postgresql-acceptance-evidence.json
│   │   ├── integration-testing.md
│   │   ├── performance-testing.md
│   │   ├── postgresql-acceptance-evidence.json
│   │   ├── private-history-read-acceptance-evidence.json
│   │   ├── provider-safety-acceptance-evidence.json
│   │   ├── public-guidance-acceptance-evidence.json
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
│   │   ├── c4-provider-safety-delivery.md
│   │   ├── c5-private-history-read-delivery.md
│   │   ├── d2-arabic-engineering-delivery.md
│   │   ├── d3-public-guidance-delivery.md
│   │   ├── data-boundary-repair.md
│   │   ├── identity-foundation-engineering-delivery.md
│   │   ├── option-a-engineering-delivery.md
│   │   └── q1-ci-runtime-delivery.md
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
│   │   │   ├── HistoryPage.test.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── NotFoundPage.tsx
│   │   │   ├── PublicPages.test.tsx
│   │   │   ├── PublicPages.tsx
│   │   │   └── history.integration.test.tsx
│   │   ├── services
│   │   │   ├── analysis.ts
│   │   │   ├── history.ts
│   │   │   └── http.ts
│   │   ├── styles.css
│   │   ├── styles
│   │   │   └── tokens.css
│   │   ├── test
│   │   │   ├── history.ts
│   │   │   ├── results.ts
│   │   │   └── setup.ts
│   │   ├── types
│   │   │   ├── analysis.ts
│   │   │   ├── explanation.test.ts
│   │   │   ├── explanation.ts
│   │   │   ├── history.test.ts
│   │   │   └── history.ts
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
    ├── test_ci_policy.py
    ├── test_design_tokens.py
    ├── test_postgres_acceptance.py
    ├── test_requirements.py
    ├── test_smoke_container.py
    ├── test_verify.py
    └── verify.py
```

