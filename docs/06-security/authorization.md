---
title: Authorization
document_id: DOC-06-AUTHORIZATION-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-30
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Authorization
## Purpose
Define standards for Authorization.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
Least privilege is required. Exactly one configured founder identity with verified MFA may access the Command Center. Customers have no administrative entitlement; employee roles and delegated administrative access are not required for initial release. Provider-neutral dependencies are tested but not attached to new production routes.

See [approved policy and implementation limits](../06-security/identity-access-foundation.md)
for the exact founder approval, existing code, adapter obligations and remaining gates.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Recorded explicit founder identity/deployment approval without approving a vendor or claiming complete implementation.
- 1.0.0 — Initial proposed specification.
## Approval
The 2026-10-30 founder approval covers the boundaries stated above; remaining implementation/vendor/release details are not approved by implication.
