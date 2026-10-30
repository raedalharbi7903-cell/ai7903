---
title: Safe HTTP Request Observability
document_id: DOC-HTTP-OBS-001
version: 1.0.0
status: implemented-local-verified-hosted-pending
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-31
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Safe request observability

## Purpose

Expose useful operational request status/duration without collecting customer
request contents or introducing a new exporter, account tracker or Command Center.

## Scope

The existing app factory installs a small ASGI middleware using existing structlog.
No HTTP response contract, engine methodology, identity or dependency changes.
Console logging is operational evidence, not durable incidents/audit/financial data.

## Main content

http_request_finished contains six bounded scalar fields: server-generated UUID,
allowlisted HTTP method (otherwise OTHER), matched Route template (unmatched fixed
label), actual sent status, monotonic duration_ms and unhandled exception category.
No raw path, query, headers, body, owner/email/session or caller-supplied request ID.

Streaming/non-HTTP messages pass through. Logging failure cannot mask the original
application/transport failure or change a response. Cancellation before headers has
unknown status; after headers preserves sent status. A finished event is not proof
the response body completed or reached the customer.

With the current FastAPI/Starlette stack, the middleware is inside ServerErrorMiddleware:
an unhandled exception before headers records500 according to the registered safe
handler, then reraises untouched. After headers the sent status remains. Alternate
outer custom non500 handlers would require reviewing this integration assumption.

### Native server log hardening

Safe JSON500 alone did not prevent Uvicorn from logging the rethrown exception's
raw message/traceback. An actual installed H11 RequestResponseCycle test proved
leakage before the fix. Central logging now installs one idempotent uvicorn.error
filter for records containing traceback/cached exception/stack fields. It retains
severity and a bounded safe error class in JSON while removing raw message,
arguments, traceback and caches. Ordinary server messages and app JSON/loglevel
behavior remain. Errors are still recorded, not silently discarded.

Packaged Uvicorn, Makefile/local setup and isolated HTTP test servers explicitly
use --no-access-log: default native access logs would otherwise expose raw
paths/query independently of safe middleware. A source-policy guard and owned
container query-probe check prevent accidental packaged regression. The container
check inspects stdout AND stderr. No real user data is used.

This does not certify pre-lifespan startup logging, reverse-proxy/platform/access
logs, external collectors, log retention/access or arbitrary operator overrides.
Those remain release/security review tasks; do not claim complete privacy compliance.

### Verification

29 new request telemetry tests plus nine existing error/security cases passed.
Nine new native-server redaction tests include actual Uvicorn/H11 safe500 response
and formatted logs, cached fields, exception groups, unsafe classes, idempotent
configuration and retained application logging. Five original redaction cases
failed before the repair. Final backend run:718 PASS in35.73s; Ruff/Black/compile
PASS. Seven actual frontend/API tests PASS in7.98s after middleware/startup change.
Frontend type/lint/format/build PASS. Tooling29 PASS including packaged access-log
guard. Previous source efda7d4 hosted18 PG cases and full gates PASS; this package
requires its own source-specific hosted receipt before claiming container acceptance.

## Related documents

- [Source-specific prior integration evidence](../10-testing/resumed-foundations-hosted-evidence.json)
- [Canonical requirements](../02-product/canonical-requirements.json)
- [Previous implementation delivery](../delivery/resumed-customer-analysis-delivery.md)

## Change history

- 1.0.0 — Bounded operational request events and proven native exception-log repair.
