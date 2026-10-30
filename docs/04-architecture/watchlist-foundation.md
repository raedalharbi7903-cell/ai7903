---
title: Private Watchlist Workflow
document_id: DOC-WATCHLIST-001
version: 1.0.0
status: implemented-release-gated
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-31
next_review: 2026-11-30
related_documents: [DOC-HISTORY-001, DOC-SEC-IDENTITY-FOUNDATION-001]
---

# Private watchlist

## Purpose

Implement CUSTOMER-17 as an actual owner-scoped preference workflow, not a market
scanner, price feed, alert service or implicit analysis request.

## Scope

The existing SQLAlchemy/session/service/identity/audit architecture and React
router are reused. No vendor, real identity, privacy policy or final visual
decision is selected. Both ordinary API and frontend default to unavailable
protected access until a reviewed identity adapter and policies are supplied.

## Main content

### HTTP contract

- GET /api/v1/watchlist: contract_version 1.0, items and next_cursor.
- POST /api/v1/watchlist: strict pair/timeframe only. New preference returns 201;
  existing active owned duplicate returns the unchanged item with 200.
- DELETE /api/v1/watchlist/{UUID}: owned unexpired deletion, 204; missing, foreign
  and expired resources share generic 404.

Items contain id, pair, timeframe, created_at and expires_at. No owner, credential,
market price or analytical output. Pair follows existing uppercase spot-pair
syntax, length 3–32. Timeframes: 1m, 5m, 15m, 1h, 4h, 1d; fixture is not supported.
A pair label is not evidence that a provider lists or licenses that instrument.

Listing uses existing limit 1–100 (default20) and paired before_created_at/before_id,
ordered by creation time and UUID descending. Unknown owner/role/query fields fail.
A full final page may have a continuation hint followed by an empty page.

### Security and transactions

WATCHLIST_ENABLED defaults false. Retention duration/policy reference must be
explicit, separate from history. Mutations also require WATCHLIST_ALLOWED_ORIGIN
and separate audit retention/reference. None has a default approval or duration.
Trusted identity and policy checks run before DB construction. Exact single Origin
plus cross-site rejection reuses the unchanged history helper; Origin is not identity.

Owner keys use existing issuer+subject hashing and verified-email/session revalidation.
Unique owner/pair/timeframe constraint handles concurrent duplicate insert with a
savepoint. Duplicate responses never renew expiry or add duplicate success audit;
both duplicate paths revalidate identity and item expiry after DB work.

Create/delete and minimal pseudonymous audit commit atomically. Audit/commit failure
or session expiry rolls back both. No raw result/email/secret in audit. This is
application append-only writing, not tamper-proof storage. Additive migration0004
does not alter history/audit schemas; downgrade drops watchlist data only.
No production migration was run.

### Arabic workflow

/watchlist loads only on user action. Save is explicit, delete has cancel/confirm,
success waits for verified response/204. Safe loading/error/empty states, cancellation
and no-store same-origin transport are retained. Authorization failure clears
private data. There is no token/localStorage fake login or automatic scan.

Selecting a saved pair navigates to the existing synthetic analysis form and
prefills validated pair/timeframe only. It does not send an analysis request.
Six existing backend timeframes now have matching synthetic UI intervals; fixture
prices remain explicitly synthetic, not a live price for the named pair.

### Verification and limits

- backend/tests/test_watchlist_service.py and tests/api/test_watchlist.py cover
  ownership, expiry, strict copied models, policies/origins, audit rollback and duplicates.
- backend/integration/test_postgres.py adds genuine two-session concurrent insert,
  actual API, constraint rollback and migration preservation; own-source hosted
  execution is required before claiming PostgreSQL acceptance.
- frontend WatchlistPage/types tests and watchlist.integration.test.tsx use
  component states and real isolated FastAPI HTTP. Synthetic verifier is test-only,
  refuses non-testing startup and is excluded from the production image.
- scripts/smoke_container.py checks production-image GET/POST/DELETE denial with
  forged and exact test-only tokens. Restore compares nonempty watchlist contents.

Still incomplete: real identity/revocation/recovery, privacy/legal consent and
retention/physical erasure/backups, rate/abuse and capacity policy, full browser/a11y/
visual acceptance and production enablement. Timeout is not guaranteed server
cancellation; duplicate idempotence is not general request idempotency.

## Related documents

- [History architecture](analysis-history-foundation.md)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [Canonical traceability](../02-product/canonical-requirements.json)

## Change history

- 1.0.0 — Implemented explicit private preferences with bounded verification.
