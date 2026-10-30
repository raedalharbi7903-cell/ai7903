---
title: Disposable PostgreSQL Acceptance
document_id: DOC-DB-POSTGRES-ACCEPTANCE-001
version: 1.0.0
status: verified-disposable-ci-scope
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Disposable PostgreSQL acceptance

## Verified hosted result — 2026-10-30

Run [41058711415](https://github.com/raedalharbi7903-cell/ai7903/actions/runs/41058711415)
at 12e22e178232dfd77e7ec9a02b2e562563d54440 completed SUCCESS:
six actual PostgreSQL tests passed in 2.04s and pg_dump/restore/migration checks
passed. Full-stack gates and backend container smoke also passed.
[Retained evidence](../10-testing/postgresql-acceptance-evidence.json).
Pending wording in the original execution notes below records pre-push state;
this result closes disposable-CI verification only, never production acceptance.

## Purpose

Verify the intended database through actual PostgreSQL, not infer it from SQLite.

## Scope

DB-PG-ACCEPTANCE and G08. CI-only disposable database, not production hosting,
customer-data isolation, approved retention, RPO/RTO or deployment acceptance.

## Main content

Psycopg 3.3.6 (binary extra) is pinned alongside unchanged SQLAlchemy 2.0.43.
The [official package](https://pypi.org/project/psycopg/) supports Python 3.12;
SQLAlchemy documents the [postgresql+psycopg dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg).
Driver installation, import and pip check pass locally. Dependencies retain their
own licenses; production redistribution/security review is not waived.

scripts/postgres_acceptance.py creates its own random database name and password.
It never uses a caller's DATABASE_URL, mounts no host files, binds only loopback
on an ephemeral port, bounds resources and pins the official PostgreSQL 17.11
bookworm image by OCI index digest. Digest source:
[official image metadata](https://github.com/docker-library/repo-info/blob/master/repos/postgres/remote/17.11-bookworm.md).
The wrapper supplies password through environment inheritance, never command text,
does not set host trust authentication and does not write credentials to evidence.
Only the exact validated container ID is removed; tmpfs test data is disposable.

It runs backend/integration/test_postgres.py explicitly. That module is outside
the ordinary SQLite test path and refuses non-owned/non-loopback/non-testing
configuration rather than silently skipping. Tests exercise the existing engine/
session factory: actual Psycopg/PostgreSQL connection, Alembic upgrade/downgrade,
no hidden commit, exception rollback, constraints, parameter/Arabic text binding,
no dirty reads and 32 bounded concurrent atomic updates.
The script then uses pg_dump/pg_restore into a second owned database and checks
the original backup snapshot plus migration revision.

The .verification/postgres-acceptance.json report is written only after actual
tests and restore succeed, without the database URL/password. Hosted CI runs the
harness as an explicit failing step and preserves artifacts. Unit tests mock Docker
only to prove ownership/cleanup/credential handling; they do NOT prove runtime DB
or backup acceptance. Local Docker remains unavailable.

Reports start RUNNING and become PASS only after tests, restore and exact owned
cleanup all succeed. Failures replace stale success; absent Docker is NOT VERIFIED.
Mock-only tests intercept artifact writes so synthetic success is never persisted
as real runtime evidence. TCP readiness avoids initdb's temporary socket-only server.

Configuration now recognizes development/testing/staging/production. Staging and
production both deny demo analysis; existing production contract is unchanged.
No production database, paid service, public authentication route or business
table migration was created. No launch or hosting approval is inferred.

Focused configuration/API/migration tests passed 34 cases. An earlier unprivileged
run had four Windows temp-directory setup errors; rerunning with appropriate
permissions resolved those errors, but the legacy pytest cache emitted an
access-denied warning. Full checkpoint verification uses the established dedicated
cache. Pip printed an available-upgrade notice; no unrelated pip/toolchain update
was made. Hosted execution remains required before asserting PostgreSQL acceptance.

Run from root using the backend virtualenv:
`backend/.venv/Scripts/python scripts/postgres_acceptance.py` (Linux: bin/python).
Docker must be installed. Never point this harness at an existing database or
manually spoof its ownership guard. Actual production roles, TLS, encryption,
customer isolation, retention, scheduled backups and recovery objectives remain
separate release requirements.

## Related documents

- [Canonical register](../02-product/canonical-requirements.json)
- [Verification runbook](verification-runbook.md)
- [Original handover gaps](../handover/REMAINING_WORK.md)

## Change history

- 1.0.0 — Added the driver, four-environment boundary and owned PostgreSQL CI tests.
