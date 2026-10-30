---
title: C5 Protected History Read Engineering Delivery
document_id: DOC-DELIVERY-C5-001
version: 1.0.1
status: verified-local-and-hosted-protected-read
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-API-HISTORY-001, DOC-HISTORY-001]
---

# C5 delivery

## Hosted publication receipt

Source e53a80863236b99ee2090c8c9e4c639436b67570, run 41097056519 completed
SUCCESS: all 17 gates, nine actual PostgreSQL tests including registered private
HTTP read, dump/restore and production-image arbitrary/test-only token denial.
[Retained evidence](../10-testing/private-history-read-acceptance-evidence.json).
This supersedes precommit pending entries below; real identity/privacy/customer
write/production approval remains incomplete. No main merge or paid resource.
Actual PG summary: nine PASS, one Starlette/AnyIO deprecated BlockingPortal alias
warning, 2.54s. Hosted actions also warn about Node 20 targeting/forced Node 24,
punycode/url.parse deprecations; image build pip-root warning is build-time only
and non-root runtime passed. None suppressed. Dependency/action compatibility
repair remains follow-up work, not a hidden clean-warning claim.

## 1. Executive summary

IMPLEMENTATION IN PROGRESS. Connected genuine stored existing-pipeline results to
protected metadata/detail GET API and Arabic /history UI. Added shared strict
adapter-claim validation, bounded metadata-only pagination, safe shared HTTP client,
no-store/cancellation and real positive/default-denied HTTP integration.
Repaired corrupt historical timestamp defaulting.
Not complete: real identity/login/recovery/revocation, consented saving/public
deletion/purge, durable audit/CSRF mutations, retention/erasure/rate limits,
founder design/browser and production activation. No platform-completion claim.

## 2. Architecture decisions

Green: strict revalidation of copied/constructed trusted session models; finite,
complete, aware original saved result validation; metadata-only SQL and safe errors.
Yellow: additive protected GET routes, versioned metadata DTO/query, explicit
default-off history/policy configuration, frontend route and shared transport.
Existing FastAPI 0.116.1/Pydantic/SQLAlchemy/sequential AnalysisService/React stack
retained. No new dependency/migration, provider, role, decision formula or second pipeline.
Existing API body/error/analysis contract preserved; new approved customer-history
read interface described in docs/08-api/history-api.md. No client owner input.

Authentication and configuration gates precede database construction. Customer
MFA is not required; genuine boolean false remains valid for customers. Founder
still needs exact enrolled identity and true MFA. Revalidation is not vendor
signature/revocation proof. Test identity exists only in test source, not app image.
Read requests never save/reanalyze/commit/delete. Write workflows deliberately
remain unfinished pending atomic audit/CSRF/consent integration, not marked complete.
Trade-offs: metadata list requires explicit detail read, full page may yield empty
continuation, no final browser/copy/design or production auth certification.

## 3. Repository tree

Complete current tracked/nonignored source tree below, no collapsed directories.
Ignored dependencies/build/cache and Git internals excluded, historical recovery
artifacts and previous source preserved.

## 4. File change report

Added:
- backend/app/api/v1/history.py
- backend/app/dependencies/history.py
- backend/app/schemas/history.py
- backend/tests/api/test_history.py
- backend/tests/http_history_fixture.py
- docs/08-api/history-api.md
- frontend/src/pages/HistoryPage.test.tsx
- frontend/src/pages/HistoryPage.tsx
- frontend/src/pages/history.integration.test.tsx
- frontend/src/services/history.ts
- frontend/src/services/http.ts
- frontend/src/test/history.ts
- frontend/src/types/history.test.ts
- frontend/src/types/history.ts
- docs/delivery/c5-private-history-read-delivery.md

Modified:
- IMPLEMENTATION_PLAN.md
- PROGRESS.md
- PROJECT_SPEC.md
- docs/10-testing/requirement-evidence-matrix.md
- .env.example
- backend/app/api/v1/router.py
- backend/app/config/settings.py
- backend/app/repositories/analysis_history.py
- backend/app/security/dependencies.py
- backend/app/security/identity.py
- backend/app/services/analysis_history.py
- backend/integration/test_postgres.py
- backend/tests/security/test_identity_boundaries.py
- backend/tests/test_analysis_history.py
- docs/02-product/canonical-requirements.json
- docs/04-architecture/analysis-history-foundation.md
- docs/06-security/identity-access-foundation.md
- docs/README.md
- frontend/README.md
- frontend/src/app/App.tsx
- frontend/src/layouts/Layout.tsx
- frontend/src/services/analysis.ts
- frontend/tests/api-setup.ts
- scripts/smoke_container.py

Deleted: none. Renamed: none.
History DTO definitions moved into app/schemas/history.py and remain imported by
the service, preserving its exposed names/valid output shape. No valuable work reset.

## 5. Git report

Branch feature/crypto-analysis-validation.
Baseline 39c408fd8e2709554fb5e2d4998d5d19aee593fa, confirmed clean before changes.
Commit message: feat: connect protected history reads with strict identity validation.
New hash/push/source-specific CI must be verified after publication.
No merge/main/force push, paid vendor commitment or production activation.

## 6. Validation report

Full command: backend/.venv/Scripts/python scripts/verify.py.
First integrated checkpoint before two final snapshot tests: all 17 PASS,
478 backend (25.43s), 65 frontend (12.68s), 24 tooling (0.158s).
Final clean post-repair checkpoint PASSED all 17 gates: 480 backend (26.53s),
65 frontend (12.57s), 24 tooling (0.163s), including the repaired documentation gate.

| Validation | Evidence |
| --- | --- |
| Strict session/history focused | PASS — 68 after session repair |
| API/core/session focused after snapshot repair | PASS — 91, 3.41s |
| Existing/new actual HTTP frontend | PASS — included in first 65-test checkpoint |
| TypeScript/ESLint/Prettier/build | PASS — final clean full run, build 405ms |
| Ruff/Black/import/compile/pip/frozen install/peers | PASS — final clean full run |
| Documentation links | PASS — zero issues after completing report, then final full run |
| Actual generated OpenAPI | PASS — only intended reads/query fields/metadata |
| Requirement integrity | PASS — five, 0.103s after traceability edits |
| Container/actual PostgreSQL local | NOT VERIFIED — Docker unavailable |
| New hosted actual PostgreSQL HTTP test | PENDING — nine server tests expected, not a claimed result |
| New hosted full stack/container token denial | PENDING source-specific run |
| Backend independent mypy/Pyright | NOT CONFIGURED; no false type-check claim |
| Actual external identity/browser/production | NOT VERIFIED |

Failures repaired:
- Seven malformed copied-session regression cases failed before shared validation.
- Repository list method shadowed list type annotations in new list_headers;
  deferred annotation evaluation fixes the root import error, no suppression.
- Initial Ruff import/line issues repaired with existing formatters.
- Two strict snapshot tests failed (naive generation timestamp accepted, incomplete
  stored record returned 200 with a new default timestamp); repaired before final run.
- A later documentation-link check found two links to this not-yet-created report;
  report completed, standalone link audit zero, then all 17 gates passed on a clean run.
No assertion removed, raw error exposed or validation bypass introduced.

The positive frontend HTTP server is test-only, uses real stored pipeline output,
and refuses non-testing startup. Ordinary app has no synthetic verifier.
Container acceptance now checks both forged and exact test-only tokens are denied.

## 7. Definition of done

- Completed: default-denied protected list/detail API and explicit policy gates.
- Completed: real owner/issuer/expiry isolation, validated keyset query and no owner field.
- Completed: metadata-only SQL, original full result only on explicit detail read.
- Completed: strict original finite/aware/complete stored snapshot validation.
- Completed: actual Arabic UI with load/empty/error/detail/page/cancel states.
- Completed: no mock login, fabricated records, new analysis on read or token storage.
- Completed: shared safe transport preserves existing analysis error alias/behavior.
- Completed: positive real HTTP integration and actual ordinary-app denial.
- Completed: final clean integrated local run.
- Pending: source-specific hosted PG/container acceptance.
- Not completed: full customer history writes/deletion/audit/auth/privacy/visual lifecycle.
CUSTOMER-16 and authentication remain PARTIALLY IMPLEMENTED.

## 8. Known issues

Real identity vendor and lifecycle remain absent, so actual default API denies access.
History flag is false; configuration alone is not privacy/founder approval.
No public saving, deletion or purge HTTP endpoint; existing private service is retained.
No consented automatic storage, durable read/write audit, rate limiting or full
retention/backups erasure. No approved full customer account or design/browser UX.
Shared HTTP uses modern AbortSignal timeout/any; browser support matrix needs review.
Errors are safe and successful private responses no-store; no comprehensive privacy
or cross-session logout certification before vendor integration is claimed.

## 9. Breaking changes

No breaking existing public analysis/health change. Additive GET history interface.
Invalid copied adapter claims and invalid/corrupt snapshots now fail closed.
Legacy AnalysisClientError export remains an alias of the shared safe error class.
No database revision/dependency changes or production database altered.

## 10. Performance and security notes

Header queries exclude result blobs, capped at 100/default20; detail snapshot retains
1 MiB storage bound. Shared transport combines timeout with caller cancellation.
No benchmark claim. First integrated build JS 288.16 kB/gzip90.91 kB.
Only synthetic identities/data in tests, no licensed market acquisition, external AI,
payment, cookie/token minting or secret committed. No customer/founder role bypass.
Real provider signature/revocation/recovery/CSRF review remains a separate gate.

## 11. CTO recommendations

Complete atomic audited consented save/delete workflows before activating customer
history. Select/review identity and privacy/retention policy; do not infer approval
from synthetic configuration references. Keep production-image test-token denial
and actual PostgreSQL HTTP tests. Review browser/accessibility/copy/design.

## 12. Questions for CTO

No new sensitive decision was invented. Identity vendor/assurance/recovery,
retention/erasure/privacy, session/logout policy and final customer visual direction
remain unresolved. No paid resource, data transfer or production launch performed.

## 13. Next sprint readiness

Continue current full-platform goal, not another sprint or completion declaration.
Next dependency-aware package: consented saving and atomic durable audit/deletion/
CSRF workflows, then owned watchlists/account/support/commercial/Command Center
scope. Preserve real provider/privacy/release gates while completing internal work.

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
    ├── test_design_tokens.py
    ├── test_postgres_acceptance.py
    ├── test_requirements.py
    ├── test_smoke_container.py
    ├── test_verify.py
    └── verify.py
```

