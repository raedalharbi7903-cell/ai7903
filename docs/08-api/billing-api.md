---
title: Billing API Contract
document_id: DOC-API-BILLING-001
version: 1.0.0
status: implemented-default-off-provider-unconfigured
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-11-05
next_review: 2026-12-05
related_documents: [DOC-BILLING-001]
---

# Billing API

## Purpose

Describe additive billing resources, not imply a working payment provider or charge.

## Scope

All paths below have /api/v1 prefix. Customer resources require trusted identity
and explicit policies; ordinary application verifier defaults deny. Event ingress
has independent provider verification, not customer-role authorization.

## Main content

| Method/path | Input | Result |
| --- | --- | --- |
| GET /billing/subscription | None | SubscriptionSummary1.0 |
| GET /billing/history | limit1–100/default20; pairedbefore_created_at/before_id | BillingHistoryPage1.0 |
| POST /billing/subscription/cancel | Strict{} JSON, exact Origin | Recorded local cancellation summary |
| POST /billing/events | Opaque rawbytes max65536, reviewed adapter authentication | Receipt{id,processing_status,duplicate} |

Summary fields: plan monthly; state none/active/scheduled/expired/review_required;
entitled boolean; paid_period_start/end aware or bothnull; cancellation/renewal/
review booleans. Reviewstate can coexist with valid current paidaccess; it does
not itself revoke an already confirmed window. End is exclusive.

History: items{id,kind,amount_minor,currency,recorded_at,retained_until,
processing_status}, next_cursor existing{created_at,id}|null. amount_minor is a
positive canonical decimalstring ornull, never a JSON float. No default currency/
exponent or tax invoice. Money fields are paired, provider event IDs omitted.

Known HTTP statuses:401 untrusted identity/signature,403 denied Origin,404 absent
owned cancellation resource,409 safe retry,413 event too large,422 invalid input,
503 disabled/missing policy/unconfigured or unavailable provider. Errors use the
existing safe structure. Configured provider strings cannot install/approve an
adapter; rawJSON cannot become VerifiedBillingEvent through a public schema.

Cancellation is LOCAL intent only until approved provider delivery is implemented.
No restore-renewal/checkout/charge/refund route exists. Body parsing after gates
avoids opening DB for forbidden owner/role/financial fields. No existing analysis/
history/watchlist contract changed and no demo paywall invented.

## Related documents

- [Architecture and limits](../04-architecture/billing-foundation.md)
- [Current requirements](../02-product/canonical-requirements.json)

## Change history

- 1.0.0 — Additive default-off customer views and trusted event ingress.
