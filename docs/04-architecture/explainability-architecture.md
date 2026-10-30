---
title: Explainability Architecture
document_id: DOC-EXPLAIN-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Explainability Architecture
## Purpose
Define explainability boundary.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content

2026-10-30 runtime overlay: the historical proposal below is preserved, but its
documentation-only status no longer describes current implementation. Existing
pipeline now includes a typed Arabic deterministic fallback and final-failure
reconciliation, with frontend matching-state guards. Rich/generative explanation
and production acceptance remain incomplete. See
[current implementation](../05-analysis/arabic-deterministic-explanation.md).
Future explanation must cite structured evidence, decision context, confidence limitations, and conflicts. It must communicate uncertainty and cannot manufacture support.

**Implemented:** documentation only. **Approved Future Architecture:** this subject may be implemented only through approved work. **Decision Required:** exact algorithms, formulas, providers, permissions, and operational thresholds are not approved unless stated otherwise.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
## Approval
Proposed; CTO approval required.
