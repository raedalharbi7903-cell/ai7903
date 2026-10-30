---
title: Owner-scoped Analysis History Foundation
document_id: DOC-HISTORY-001
version: 1.1.0
status: partial-protected-read-integration
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-DB-POSTGRES-ACCEPTANCE-001]
---

# Owner-scoped history

## Current handover overlay — 2026-10-30

The original C3/C5 narrative below is preserved as historical evidence. Source
6bf6f3ce now includes previously pending explicit save/delete, separate minimal
audit_events migration 20261030_0003, atomic mutation service and exact Origin
gates. All default-deny/owner/retention boundaries remain. This is preservation,
not a new architecture selection or production enablement.
See [current implementation and limitations](../handover/CURRENT_STATE.md);
old public-mutation absence statements no longer describe current source.

## Purpose

Persist actual existing AnalysisService results without creating a second analysis
pipeline or enabling unauthenticated customer history.

## Scope

Internal SQLAlchemy repository/service and migration 20261030_0002, now connected
to protected read-only HTTP and Arabic UI in C5. No public save/deletion route,
client owner field, selected auth vendor or production enablement.

## Main content

The only principal input is a server-verified VerifiedSession. Every operation
revalidates its typed claims, verified email and expiry. The adapter remains
responsible for issuer/audience/signature, current revocation and session lifecycle;
this service cannot prove those from a constructed Python object. Never populate
VerifiedSession from request JSON. The unconfigured application verifier still denies.

An SHA-256 key over an unambiguous JSON [issuer, subject] pair scopes all reads,
lists, deletes and expiry purges. This reduces raw identifier storage but is
pseudonymization, not anonymity, encryption or database row-level security.
There is no founder bypass, cross-customer lookup or caller-selected owner.

History is disabled by default: no HistoryPolicy, no reads/writes or analysis
execution through analyze_and_record. A trusted deployment must explicitly supply
a positive duration and policy approval reference; no production duration or
privacy approval is invented. Synthetic test durations are not recommended policy.
A reference is configuration traceability, not cryptographic proof of legal consent.

record serializes the validated result snapshot only, not the original raw request,
credentials or email. Pre-JSON nonfinite checks prevent Pydantic null conversion.
Snapshots are bounded to 1 MiB UTF-8, pages/purge batches to 100 entries, default
page 20. These are resource bounds, not billing entitlements or analytical limits.
The repository flushes but never commits: the caller owns transaction/rollback.
Returned result objects are independent of stored and input snapshots.

Keyset ordering is created_at DESC, UUID DESC, including equal-timestamp ties.
Expiry is exclusive: expires_at <= now is never readable. Owner-only hard delete
is idempotent; bounded purge_expired deletes only that owner's expired rows.
It does not create a global maintenance job or establish compliant retention.
Scheduled physical erasure, backup erasure, legal holds, account deletion and
durable sensitive-operation audit remain release gates. No customer history
route should be enabled until these and actual identity/privacy review are ready.

Timestamp columns use timezone-aware UTC. PostgreSQL preserves timezone semantics;
SQLite drops metadata, so only these application-owned UTC columns are explicitly
reattached on read. Naive caller clocks/cursors are rejected, never interpreted
as arbitrary local time. Models and migration use the same columns/indexes.

Migration is additive. Existing empty revision 20260725_0001 is preserved and tested
explicitly. New head creates analysis_history and owner-page/expiry indexes.
Downgrade deletes the history table and its data; never run it on valuable customer
data without an approved backup/recovery procedure. No production migration run here.

## Verification and remaining work

### C5 protected read integration

Registered GET /api/v1/history and GET /api/v1/history/{identifier}. Authentication
and explicit HISTORY_ENABLED/policy gates run before a database session is opened.
Default verifier remains unconfigured/deny, HISTORY_ENABLED defaults false and no
retention duration is invented. Server configuration is not proof of privacy approval.
HistoryQuery rejects extra owner/role fields, nonpositive/oversize limits and unpaired
or naive cursors. Missing, foreign and expired detail IDs share one generic 404.
Successful responses carry private, no-store. Errors contain no raw database data.

List pages select only UUID/created/expiry columns, never deserialize result_json;
full original AnalysisResult is read only on explicit detail request. Limit is 100,
default 20, with existing descending timestamp/UUID keyset semantics. A cursor on
a full page is a continuation hint and may yield an empty final page.
No read call creates/deletes records, runs analysis or commits a transaction.
Detail reads require every persisted AnalysisResult field and an aware original
generation time. Corrupt snapshots cannot acquire a fresh timestamp/defaults;
write/read both reject nonfinite data. Two failing regressions were repaired.

The /history UI reads only on explicit user action and uses shared safe transport,
same-origin credentials, no-store, bounded timeout/cancellation and validated
versioned responses. Detail response UUID must match the requested UUID. Authorization
loss clears loaded private state. No auth tokens are invented or stored in localStorage.
The actual default API returns 401; no simulated login is offered.
Test-only server/identity injection lives under backend/tests, refuses non-testing
startup and is excluded from the production image. Real HTTP positive tests use
actual stored existing-pipeline snapshots, not mocked analysis responses.

Trusted adapter outputs are now strictly revalidated at the shared identity
boundary, including copied/constructed Pydantic models that bypass validators.
Seven regression cases failed before repair. No truthy string/integer can supply
MFA/email assurance. This does not replace vendor signature/revocation verification.

C5 does not expose save/delete/purge HTTP mutations: explicit saving consent,
atomic durable audit/CSRF and complete privacy/account lifecycle remain work to
finish, not externally completed features. Internal C3 deletion/purge stays tested.
Customer history remains PARTIAL pending these and real identity/retention review.

Hosted source 638e3f8 verified: run 41068207446/job 124105117663 SUCCESS, eight
actual PostgreSQL tests (1.91s), history isolation/expiry, migration/dump/restore,
all full-stack gates and application container PASS. See
[retained evidence](../10-testing/history-postgresql-acceptance-evidence.json).

backend/tests/test_analysis_history.py covers default denial, no disabled pipeline
execution, all 28 actual pipeline outputs, owner/issuer isolation, invalid/expired/
mutated identity, keyset ties, immutable snapshots, bounded paging/deletion/purge,
nonfinite/oversize rejection and caller-owned rollback.
backend/tests/test_migration_recovery.py checks both preserved initial revision
and additive head, indexes, upgrade/downgrade/reupgrade and SQLite backup.
backend/integration/test_postgres.py adds actual server isolation and expiry-purge
tests, explicitly executed in owned CI, never represented by mocks.
The dump/restore harness now checks new head and history row count.

Remaining: saving/deletion/purge workflow, trusted auth vendor/revocation/CSRF,
approved retention/erasure lifecycle, durable audit/rate limits, complete customer lifecycle,
founder copy/visual/browser and production acceptance. Customer history is PARTIAL.

## Related documents

- [Canonical requirements](../02-product/canonical-requirements.json)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [PostgreSQL acceptance](../09-devops/postgresql-acceptance.md)
- [C3 delivery](../delivery/c3-history-engineering-delivery.md)

## Change history

- 1.1.0 — Protected read API/UI, metadata-only pagination and shared strict identity revalidation; write/audit/identity/privacy release gates remain open.

- 1.0.0 — Add default-disabled internal owner-scoped snapshot persistence.

