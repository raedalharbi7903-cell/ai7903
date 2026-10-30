---
title: Authentication
document_id: DOC-06-AUTHENTICATION-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-30
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Authentication
## Purpose
Define standards for Authentication.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
Email-based customer authentication is approved. Secure sessions and account recovery are required; vendor selection remains subject to security/cost review. The current provider-neutral verifier denies access until a reviewed adapter is configured. No login, recovery or session endpoints are implemented.

See [approved policy and implementation limits](../06-security/identity-access-foundation.md)
for the exact founder approval, existing code, adapter obligations and remaining gates.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Recorded explicit founder identity/deployment approval without approving a vendor or claiming complete implementation.
- 1.0.0 — Initial proposed specification.
## Approval
The 2026-10-30 founder approval covers the boundaries stated above; remaining implementation/vendor/release details are not approved by implication.
