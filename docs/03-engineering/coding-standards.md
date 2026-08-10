---
title: Coding Standards
document_id: DOC-ENG-CODE-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-ENG-HANDBOOK-001]
---
# Coding Standards
## Purpose
Set maintainable coding conventions using approved tooling.
## Scope
Python, TypeScript, React, configuration, and security-sensitive code.
## Main Content
Python uses type hints, Ruff, Black, small modules, explicit exceptions, and Pydantic validation. TypeScript and React use strict typing, ESLint, Prettier, components with single responsibilities, and no business logic in presentation layers. Use descriptive names; keep functions focused; avoid implicit mutation and duplicated code. Configuration, secrets, URLs, and keys come from environment variables. Structured logs must not expose sensitive data. Comments explain intent, not syntax. Dependencies require purpose, compatibility, and maintenance review.
## Related Documents
[Engineering Handbook](engineering-handbook.md)
## Change History
- 1.0.0 — Initial standards.
## Approval
Proposed; CTO approval required.
