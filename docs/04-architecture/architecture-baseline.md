---
title: Architecture Baseline
document_id: DOC-ARCH-BASELINE-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-SYSTEM-001, DOC-REPO-001]
---
# Architecture Baseline
## Purpose
Describe approved architecture without claiming future implementation exists.
## Scope
Backend, frontend, persistence, analysis, AI, APIs, and boundaries.
## Main Content
Currently implemented: FastAPI backend foundation with versioned routes, configuration, SQLAlchemy/Alembic scaffolding, repositories/services/dependencies, and a generic analysis framework; a separate React frontend foundation exists on its sprint branch. Persistence is SQLAlchemy-based; API is FastAPI-based. Current security boundary is environment-based configuration and consistent error handling. Observability currently consists of structured logs.

Approved future architecture: frontend to API to application services to analysis platform to deterministic engines to evidence to decision to confidence to AI explanation. Evidence, decision, confidence, AI, external data, and product engines are not implemented. Their detailed contracts are Decision Required. Modules communicate through explicit contracts; dependencies must point inward toward stable abstractions.
## Related Documents
[System Overview](system-overview.md), [Repository Structure](repository-structure.md)
## Change History
- 1.0.0 — Initial baseline.
## Approval
Proposed; CTO approval required.
