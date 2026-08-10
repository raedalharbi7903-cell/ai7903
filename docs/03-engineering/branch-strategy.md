---
title: Branch Strategy
document_id: DOC-ENG-BRANCH-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-ENG-GIT-001]
---
# Branch Strategy
## Purpose
Define the canonical future branch model.
## Scope
Repository branches and ownership.
## Main Content
`main` is the reviewed integration baseline. Use `feature/<scope>`, `docs/<scope>`, and `hotfix/<scope>` branches. A release-branch policy is Decision Required. Branch owners keep changes scoped, short-lived, validated, and deleted after merge. Current divergent sprint branches are a known repository condition; this document defines the future model only and does not merge or modify them.
## Related Documents
[Git Workflow](git-workflow.md)
## Change History
- 1.0.0 — Initial strategy.
## Approval
Proposed; CTO approval required.
