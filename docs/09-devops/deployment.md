---
title: Deployment
document_id: DOC-09-DEPLOYMENT-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-30
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Deployment
## Purpose
Define standards for Deployment.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
PostgreSQL is approved as the intended production database, with separate development, testing and production environments. No paid hosting service is approved. Actual deployment requires provider selection, security review and founder approval; no paid commitments are authorized. Backup retention, recovery objectives and operational ownership still need specification. SQLite/CI container evidence is not PostgreSQL deployment acceptance.

See [approved policy and implementation limits](../06-security/identity-access-foundation.md)
for the exact founder approval, existing code, adapter obligations and remaining gates.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Recorded explicit founder identity/deployment approval without approving a vendor or claiming complete implementation.
- 1.0.0 — Initial proposed specification.
## Approval
The 2026-10-30 founder approval covers the boundaries stated above; remaining implementation/vendor/release details are not approved by implication.
