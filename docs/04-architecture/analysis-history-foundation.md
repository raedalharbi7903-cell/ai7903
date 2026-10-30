---
title: Owner-scoped Analysis History Foundation
document_id: DOC-HISTORY-001
version: 1.0.0
status: partial-internal-foundation
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-DB-POSTGRES-ACCEPTANCE-001]
---

# Owner-scoped history

## Purpose

Persist actual existing AnalysisService results without creating a second analysis
pipeline or enabling unauthenticated customer history.

## Scope

Internal SQLAlchemy repository/service and additive migration 20261030_0002.
No public route, client owner field, auth vendor, history UI or production enablement.

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

Remaining: protected public API contract, trusted auth vendor/revocation/CSRF,
frontend, approved retention/erasure lifecycle, durable audit and production
acceptance. This is PARTIALLY IMPLEMENTED customer history.

## Related documents

- [Canonical requirements](../02-product/canonical-requirements.json)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [PostgreSQL acceptance](../09-devops/postgresql-acceptance.md)
- [C3 delivery](../delivery/c3-history-engineering-delivery.md)

## Change history

- 1.0.0 — Add default-disabled internal owner-scoped snapshot persistence.

