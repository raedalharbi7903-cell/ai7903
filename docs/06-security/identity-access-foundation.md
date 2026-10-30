---
title: Identity and Access Foundation
document_id: DOC-SEC-IDENTITY-FOUNDATION-001
version: 1.0.0
status: approved-boundaries-partial-implementation
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-06-AUTHENTICATION-001, DOC-07-ADMINISTRATIVE_ROLES-001]
---

# Identity and access foundation

## Purpose

Record the founder's explicit access-policy approval and distinguish implemented
boundaries from the identity-provider integration still required.

## Scope

Customers authenticate using email. Exactly one founder administrative identity
may access the Command Center, with mandatory MFA. Initial release has no employee
roles, delegated administrators, self-service admin grants or role-management UI.
The founder approval supersedes earlier statements that these roles are unknown.

## Main content

### Approved policy

- Email-based customer authentication; the approval does not choose passwords,
  magic links, passkeys or an authentication vendor.
- Command Center access is exclusively founder-only, not all authenticated users.
  Verified MFA is mandatory and cannot be replaced by email verification.
- Secure sessions, recovery, least privilege and audit logging are required.
- Vendor selection remains subject to security and cost review. No paid commitment
  is authorized by this approval.

### Implemented vendor-neutral boundary

`backend/app/security/identity.py` defines immutable, strict, timezone-aware verified
sessions and a trusted adapter protocol. This is not a request schema and must never
be populated from a request body, role header or unverified JWT payload.

`backend/app/security/dependencies.py` defaults to an unconfigured verifier that
denies every request. Customer access requires adapter-verified identity, verified
email and unexpired session. Founder access additionally requires exact issuer and
subject equality against server configuration plus adapter-verified MFA.
No role or email-string matching can promote an account to founder.

`FOUNDER_IDENTITY_ISSUER` and `FOUNDER_IDENTITY_SUBJECT` must be set through secure
deployment configuration only after verified founder enrollment. Missing/empty
values deny access. Test identities are never deployment defaults.
Provider-supplied issuer/subject must remain stable; transfer/recovery cannot
silently substitute a different administrative principal.

The dependencies are exercised through FastAPI test routers only. No customer,
login, recovery, session or Command Center route is shipped in this change.
Existing production analysis denial remains unchanged. There is no actual
authentication integration until a reviewed adapter is wired into protected routes.

Access events record boundary/assurance or denial category without tokens, email,
subject identifiers or raw adapter errors. This is minimum boundary observability,
not a complete durable/compliance audit system. Actor correlation, retention,
tamper protection and access controls require the reviewed operational integration.

### Adapter and release acceptance

The final adapter must validate signature/opaque-session authenticity, issuer,
audience, expiry, revocation and MFA assurance server-side; fail closed on outages.
It must support session rotation, logout/revocation, account recovery, rate limiting
and abuse defenses. Cookie sessions require Secure/HttpOnly attributes, reviewed
SameSite policy and CSRF protection for state changes. Browser credentials must
not be persisted in localStorage. Recovery must not bypass founder MFA.
Exact lifetimes, recovery method and MFA factor/enrollment procedure remain pending
security review, not implemented defaults.

Before release, prove actual provider login, email verification, session lifecycle,
recovery, account enumeration protection, CSRF, MFA downgrade resistance and
founder-only routing. Current tests do not certify those absent workflows.

### AI and deployment decisions approved alongside this policy

No AI provider/model or paid hosting vendor is approved. Provider-neutral design
is authorized; recommendations may be prepared based on security, reliability,
performance and cost, but paid commitments need founder approval.
Customer data must not be sent to external AI until privacy/data-sharing approval.
AI remains subordinate to deterministic safety; its current unavailable state is
preserved rather than replaced with invented narratives.

PostgreSQL is the intended production database, with separate development, testing
and production environments. Existing SQLite tests do not prove PostgreSQL runtime,
backup or restore acceptance. Production hosting selection, deployment, security
review and founder release approval remain gates. No production service was
provisioned and no database migration/driver replacement was made by this package.

Market-data rights remain unresolved: the answer to that question repeated the
authentication approval and did not name a dataset or grant any license.

## Related documents

- [Acceptance dependencies](../03-engineering/acceptance-dependencies.md)
- [Authentication](authentication.md)
- [Authorization](authorization.md)
- [Administrative roles](../07-organization/administrative-roles.md)
- [Deployment](../09-devops/deployment.md)
- [Environment separation](../09-devops/environments.md)
- [Requirement evidence](../10-testing/requirement-evidence-matrix.md)

## Change history

- 1.0.0 — Recorded explicit founder policy and provider-neutral deny-by-default
  boundary; retained vendor/privacy/deployment/rights gates.
