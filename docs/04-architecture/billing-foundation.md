---
title: Provider-Neutral Subscription and Billing Foundation
document_id: DOC-BILLING-001
version: 1.0.0
status: implemented-default-off-production-blocked
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-11-05
next_review: 2026-12-05
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Subscription and billing foundation

## Purpose

Implement approved monthly lifecycle, owned billing views and durable event
integrity without choosing a provider, taking payments or approving a price.

## Scope

Single monthly tier, no launch trial/annual plan. No169SAR or other defaultprice.
No checkout/capture/charge/refund endpoint, tax invoice, assumed minor-unit exponent,
30-day month, grace period, provider cancellation delivery or analysis-paywall change.
Actual identity/payment/accountmapping/legal/privacy policies remain release gates.

## Main content

### Layers and storage

Existing SQLAlchemy/service/repository/audit architecture retained. Additive
20261105_0005 creates billing_subscriptions and billing_events only. Unique owner
and provider/event ID constraints plus row locks/versioning prevent silent lost
updates; genuine concurrent conflicts return safe409 requiring retry. No hidden
commit or second database. Mutations and minimal audit share one transaction.

Subscriptions store the last confirmed explicit UTC paid window, consent/cancellation,
administrative review flag, version and purpose-specific retention metadata.
Ledger stores bounded normalized event fields/fingerprint, not raw payload,
signature, card/email or credentials. Amounts use positive signed64-bit integer
minor units internally and canonical decimal STRINGS in public history: no JavaScript
rounding and no inferred currency exponent. Currency syntax is not approved support.

### Trusted event boundary

Constructing VerifiedBillingEvent does NOT prove signature/account mapping.
A separately reviewed adapter must verify exact raw bytes, provider-specific
timestamp/replay policy and trusted customer mapping before producing that model.
PublicJSON owner/role/payment fields never authorize a grant.

BILLING_ENABLED defaultsfalse. Purpose/audit retention references/durations,
origin and provider ID/approval reference have no defaults. References record
configuration traceability, not proof of founder/legal approval. Default verifier
always rejects, even if an operator fills provider settings. No vendor adapter is
installed; no external calls or financial commitments occur.

POST /api/v1/billing/events is opaque, streamed and capped64KiB, including absent/
false Content-Length. Default gates run before body/DB. A trusted adapter's strict
result is revalidated and must match configured provider. Bad authentication401,
outage503, invalidbody400/422, oversize413, concurrentretry409; no raw error echo.

### Lifecycle invariants

Only verified normalized paid events can establish/extend a positive explicit
paid window. Access requires start<=now<end; no grace. Failure alone never grants
or shortens paid access. Renewals need recorded consent and cannot silently
reenable cancellation. Unsupported/future/overlapping/conflicting/late-cancel
events are quarantined, cannot grant/extend and require reviewed reconciliation.

Quarantine is administrative uncertainty, NOT permission to revoke an already
confirmed window. Current access remains until its original end; unresolved review
still blocks new grants/extensions. Refund/dispute effects need a founder-approved
policy and actual provider integration, not an inferred automatic revocation.

Durable provider/event idempotency ignores customer visibility expiry. Same event/
fingerprint returns original receipt with no duplicate audit or access extension.
Fingerprint conflicts are reviewed rather than replacing the original financial
fact. No automatic financial purge is implemented or authorized.

### Customer API and Arabic interface

GET /billing/subscription returns version1.0 summary. GET /billing/history uses
owned unexpired events, bounded existing keyset cursor contract. Owner/provider
event ID/fingerprint are not public. Customer identity/policy gates precede DB.

POST /billing/subscription/cancel accepts strict{} only after identity/policy/
exact-Origin checks, before DB. Cancellation is idempotent local intent, revokes
local renewal consent, retains paid bounds and audits atomically. It does NOT
send anything to a payment provider, refund, delete the account or erase history.

/subscription manually loads summary/history and confirms local cancellation.
No mount-time fetch, invented successful account, price quote or purchase button.
Loading/errors clear private state; typed transport is same-origin/no-store.
History is event history, not a tax invoice; amounts explicitly labeled minorunits.
Existing demo analysis stays fixture-only and its contract unchanged.

### Verification and remaining gates

65 new core tests,63API tests and7startup-config redaction tests are included in
the integrated checkpoint. Exact final counts/results are in delivery evidence.
Actual isolated HTTP/UI tests read real SQL snapshots and record cancellation,
not mocked financial success. Test identities/HMAC keys never authenticate ordinary
application and are excluded from the production image.

Actual PostgreSQL concurrent event insert/retry/idempotency, lifecycle, audit
constraint rollback, signed test-ingress API and0004→0005 preservation/restore
cases require source-specific hosted execution. SQLite alone is insufficient.

Open: real signature/account mapping, webhook replay/read-deadline/rate controls,
provider cancellation outbox/delivery/reconciliation, currency/rounding/calendar
normalization, pricing/VAT/invoices/refund/dispute policy, retention/legal hold/
physical erasure/backups, real identity/recovery/MFA, final visual/a11y/browser/
professional security and production approval. Do not enable real payments.

## Related documents

- [Canonical scope](../02-product/canonical-requirements.json)
- [Identity boundary](../06-security/identity-access-foundation.md)
- [Safe operations](../09-devops/request-observability.md)

## Change history

- 1.0.0 — Gated monthly lifecycle and verified normalized-event foundation.
