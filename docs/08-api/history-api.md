---
title: Private Analysis History Read API
document_id: DOC-API-HISTORY-001
version: 1.0.0
status: implemented-read-workflow-release-gated
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-HISTORY-001, DOC-SEC-IDENTITY-FOUNDATION-001]
---

# Private history read API

## Purpose

Expose genuine previously stored analysis without new analysis execution, owner
selection from client input, or fabricated account/data availability.

## Scope

GET /api/v1/history and GET /api/v1/history/{identifier}, frontend /history.
No public save/delete/purge, login, synthetic production session or external provider.

## Main content

### Access and release gates

All reads require the trusted customer-session dependency. The default
SessionVerifier always denies. Adapter claims are revalidated, email must be
verified and session unexpired. Founder identity does not grant other owners'
records. Roles, owner headers and test tokens never authenticate the ordinary app.

HISTORY_ENABLED defaults false. Both HISTORY_RETENTION_SECONDS and
HISTORY_POLICY_REFERENCE must be explicitly configured before the read service
can be constructed; no retention duration is supplied in .env.example.
Authentication and release checks precede opening a database session.
Configuration is not proof of legal consent or founder production approval.

### Listing

Query fields only:
- limit: integer 1–100, default 20.
- before_created_at: timezone-aware timestamp, paired with before_id.
- before_id: UUID, paired with before_created_at.

Unknown query fields are rejected, including owner/role. Ordering is creation
time descending, then UUID descending. A next_cursor on a full page is a
continuation hint; an exactly full final page can lead to an empty page.

Response contract 1.0:
```json
{"contract_version":"1.0","items":[],"next_cursor":null}
```
Each item contains only id, created_at and expires_at. The SQL projection never
selects/deserializes full result_json for a list. No total count or outcome is
invented. Owner and expired filters apply to every page and cursor.

### Detail

identifier must be a UUID. Response contains id/created_at/expires_at plus the
original result using the established AnalysisResult contract. No new generated_at
is created when reading. Incomplete/nonfinite/timezone-naive persisted snapshots
fail safely instead of acquiring model defaults or fabricated timestamps.
The client rejects a response UUID different from the requested UUID.

Missing, expired and foreign entries share an identical generic 404.
Successful private reads use Cache-Control: private, no-store.
Database/native errors are safe structured responses, never raw SQL or credentials.

### Errors

| HTTP | Meaning |
| --- | --- |
| 401 | Trusted customer authentication unavailable/invalid |
| 404 | Detail unavailable, without cross-owner existence disclosure |
| 422 | Invalid UUID/cursor/limit/extra query |
| 503 | History release/policy gate not configured |
| 500 | Safe internal/storage failure |

POST and DELETE are not registered and return method-not-allowed. Read operations
do not commit, save, purge or run an analysis. Existing internal deletion remains
a separate unfinished public workflow, not silently exposed without audit/CSRF.

### Frontend

/history loads only after a user action. It lists metadata, opens a stored original
result and supports cursor continuation and returning to the current list.
Same-origin credentials/no-store and timeout plus unmount cancellation are explicit.
Authorization loss clears loaded records. No token/localStorage, mock login or
fake successful empty account is used. The default actual API returns 401.

Tests run a second isolated loopback server from backend/tests/http_history_fixture.py.
Its synthetic verifier refuses non-testing startup and is not in the production
image. Only the test harness adds its synthetic Authorization header; production
frontend source never does. Positive HTTP tests use real existing AnalysisService
snapshots and real persistence, with no mocked analysis/HTTP response.

### Security/operational limitations

Not complete: actual vendor login/recovery/revocation/logout UI, account lifecycle,
write consent, atomic durable audit, write CSRF, rate limits, physical erasure/
backup retention, full browser/a11y/founder design and production approval.
Do not enable customer use before these release gates are resolved.
No live data, external AI, payment or commercial compliance claim.

Existing request-scoped sessions are retained; no unsupported dependency upgrade
is introduced. Lifecycle reference: [FastAPI dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/).
Future mutations require a reviewed CSRF policy; origin identifies scheme/host/port,
not identity ([MDN Origin reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin)).
Neither document approves a vendor or replaces actual security testing.

## Verification

- backend/tests/api/test_history.py: actual registered router, owner/expiry/cursor,
  safe errors, release/auth before DB, metadata-only SQL and corrupt snapshot.
- backend/tests/security/test_identity_boundaries.py: strict copied-claim denial.
- backend/tests/test_analysis_history.py: service/paging/transaction/snapshot guards.
- backend/integration/test_postgres.py: additional actual PostgreSQL HTTP read case.
- frontend/src/pages/history.integration.test.tsx: positive real HTTP plus default denial.
- frontend/src/pages/HistoryPage.test.tsx and src/types/history.test.ts: states,
  validation, safe errors, cancellation, authorization loss and response identity.
- scripts/smoke_container.py: production image denies arbitrary and test-only tokens.

## Related documents

- [History architecture](../04-architecture/analysis-history-foundation.md)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [Requirement evidence](../10-testing/requirement-evidence-matrix.md)
- [Delivery report](../delivery/c5-private-history-read-delivery.md)

## Change history

- 1.0.0 — Protected read workflow and explicit unfinished write/identity/privacy gates.

