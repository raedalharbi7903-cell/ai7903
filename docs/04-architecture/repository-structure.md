---
title: Repository Structure
document_id: DOC-REPO-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-ARCH-BASELINE-001]
---
# Repository Structure
## Purpose
Describe current and reserved repository areas.
## Scope
Repository organization only.
## Main Content
Implemented backend areas: API, config, core, database, dependencies, logging, models, repositories, schemas, services, tests, and Alembic. The analysis module exists on its separate Sprint 3 branch. Frontend implementation exists on its separate Sprint 1B branch. `database`, `docker`, `scripts`, and `.github` are reserved or foundation areas; they do not imply completed services. `docs` holds governance and architecture records. Divergent branches are not treated as merged architecture.
## Related Documents
[Architecture Baseline](architecture-baseline.md)
## Change History
- 1.0.0 — Initial structure record.
## Approval
Proposed; CTO approval required.
