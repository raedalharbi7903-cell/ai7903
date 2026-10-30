---
title: Environments
document_id: DOC-09-ENVIRONMENTS-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-30
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Environments
## Purpose
Define standards for Environments.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
Separate development, testing and production environments are required. Use isolated credentials, databases and configuration; never use customer production data in fixtures or send it to unapproved AI services. PostgreSQL is the intended production database; SQLite remains the existing disposable test backend, not proof of PostgreSQL acceptance. No hosting vendor or production service is approved.

See [approved policy and implementation limits](../06-security/identity-access-foundation.md)
for the exact founder approval, existing code, adapter obligations and remaining gates.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Recorded explicit founder identity/deployment approval without approving a vendor or claiming complete implementation.
- 1.0.0 — Initial proposed specification.
## Approval
The 2026-10-30 founder approval covers the boundaries stated above; remaining implementation/vendor/release details are not approved by implication.
