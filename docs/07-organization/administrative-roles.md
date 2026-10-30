---
title: Administrative Roles
document_id: DOC-07-ADMINISTRATIVE_ROLES-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-30
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Administrative Roles
## Purpose
Define standards for Administrative Roles.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
The founder explicitly approved email-based customers and one founder-only
administrative account with mandatory MFA. Command Center access is exclusive to
that founder. No employee roles or delegated administration are required for the
initial release. This replaces the previous historical-confirmation gap, not the
separate governance responsibilities of CTO and Engineering.

Provider-neutral access dependencies are implemented/tested; actual identity,
enrollment, recovery and Command Center integration remain incomplete. See
[identity/access foundation](../06-security/identity-access-foundation.md).
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Recorded founder approval; removed obsolete unknown-role claim.
- 1.0.0 — Initial proposed specification.
## Approval
Initial identity/administrative boundary approved by founder on 2026-10-30.
Vendor/security/cost review and release approval remain required.
