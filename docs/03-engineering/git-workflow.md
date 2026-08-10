---
title: Git Workflow
document_id: DOC-ENG-GIT-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-ENG-BRANCH-001, DOC-ENG-PR-001]
---
# Git Workflow
## Purpose
Define safe repository change management.
## Scope
All tracked project changes.
## Main Content
Create scoped branches from the approved integration baseline; stage only task files; use focused commits; validate before push; use reviewed PRs; merge only after required approval. Release branches are Decision Required because no release process is approved. Rollback uses a new revert commit, not history rewriting. Prohibited practices: force-pushing shared branches, committing secrets or generated dependencies, mixing unrelated work, and destructive resets of shared history.
## Related Documents
[Branch Strategy](branch-strategy.md), [Pull Request Policy](pull-request-policy.md)
## Change History
- 1.0.0 — Initial workflow.
## Approval
Proposed; CTO approval required.
