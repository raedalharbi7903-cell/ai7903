---
title: CI Action Runtime and Pin Policy
document_id: DOC-CI-ACTIONS-001
version: 1.0.0
status: implemented-hosted-verification-pending
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-DELIVERY-C5-001]
---

# CI action policy

## Purpose

Resolve observed deprecated Node 20 action-runtime usage without changing product
dependencies, API behavior, credentials or deployment authority.

## Scope

Five existing maintained setup/checkout/artifact actions in quality.yml.
No application framework/tool version upgrade, registry authentication or paid resource.

## Main content

Each action is pinned to a full reviewed commit, not a mutable version tag.
[Baseline metadata](ci-action-baseline.json) records release/source URLs, tags,
commits and node24 runtime verified in the maintainers' action.yml.

| Existing action | Reviewed release |
| --- | --- |
| actions/checkout | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| actions/setup-python | [v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0) |
| actions/setup-node | [v7.1.0](https://github.com/actions/setup-node/releases/tag/v7.1.0) |
| actions/upload-artifact | [v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) |
| pnpm/action-setup | [v6.1.0](https://github.com/pnpm/action-setup/releases/tag/v6.1.0) |

Reviewed major-release compatibility: ESM changes are internal to these actions.
No removed setup-python pip-install input or setup-node registry/auth-token behavior
was used. Checkout remains persist-credentials false and only existing push/PR/manual
triggers remain; no pull_request_target/workflow_run privilege added.
Artifact default archive semantics, hidden evidence, fourteen-day retention and
missing-evidence failure remain unchanged. pnpm explicitly reads frontend/package.json,
keeps caching false and does not automatically install.

Python 3.12, Node 24.14.0 and pnpm 11.25.0 remain unchanged. No application dependency
or lockfile modified. Workflow token remains contents:read only, with no write/OIDC
scope or persisted credential. Full repository/actual PostgreSQL/container acceptance
remains mandatory; diagnostic startup step stays conditional on failure.

Local source policy checks verify immutable allowlisted pins, credential/trigger/
runtime/cache and acceptance settings. A local existing PyYAML BaseLoader parsed
the workflow and confirmed scoped jobs/steps/permissions. Neither check proves
remote action execution; own-source hosted run must succeed before acceptance.

Unresolved separate issue: FastAPI 0.116.1/Starlette 0.47.3 TestClient uses the
deprecated AnyIO BlockingPortal alias. No downgrade/warning filter/site-package
patch was used. Review a compatible maintained runtime upgrade independently;
do not replace a major runtime dependency or alter public behavior without the
required approval. Build-time pip-root warning is not a root application runtime:
the container's non-root boundary is tested. No clean-warning claim until logs
for the new action source are actually inspected.

## Related documents

- [Baseline](ci-action-baseline.json)
- [Delivery](../delivery/q1-ci-runtime-delivery.md)
- [C5 warning evidence](../10-testing/private-history-read-acceptance-evidence.json)
- [PostgreSQL acceptance](postgresql-acceptance.md)

## Change history

- 1.0.0 — Reviewed immutable Node 24 action pins and unchanged security/runtime scope.

