---
title: Backups
document_id: DOC-09-BACKUPS-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Backups
## Purpose
Define standards for Backups.
## Scope
Disposable SQLite recovery verification and unresolved production backup policy.
## Main Content
backend/tests/test_migration_recovery.py creates a disposable SQLite database,
applies the actual Alembic initial revision, inserts a synthetic recovery probe
only in that test database, creates a consistent backup through SQLite's backup
API, and restores it to a separate file. It verifies integrity, revision and probe
contents after modifying the original. The application still defines no business
tables; the recovery probe is not an application schema change.

This test is not evidence of scheduled backups, encrypted/offsite retention,
production restore authorization, production database recovery or an approved RPO/
RTO. Production database choice, backup target, access controls, retention,
encryption keys and recovery objectives remain Decision Required. Do not run test
reset/downgrade commands against a deployed or user database.

The same module checks upgrade/downgrade revision roundtrips, percent-containing
URLs and offline SQL without creating a database. Request-session lifecycle tests
verify rollback/close and the absence of hidden commits. Container smoke verification
applies the packaged initial revision only to a disposable /tmp database in the
container it creates; no production/user database is targeted.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Documented bounded migration/recovery verification and production limits.
- 1.0.0 — Initial proposed specification.
## Approval
Proposed; CTO approval required.
