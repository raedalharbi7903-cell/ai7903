---
title: Pull Request Policy
document_id: DOC-ENG-PR-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-ENG-GIT-001, DOC-ENG-DOD-001]
---
# Pull Request Policy
## Purpose
Define reviewable change requirements.
## Scope
All proposed merges.
## Main Content
Titles state scope; descriptions state intent, exclusions, risks, validation, and rollback. Draft PRs are used while validation or review is incomplete. Checklist: scoped diff; tests; lint; formatting; build; documentation; known limitations; no secrets; required approval. Do not merge with unresolved required checks or Red decisions. Rollback uses a revert commit.
## Related Documents
[Definition of Done](definition-of-done.md)
## Change History
- 1.0.0 — Initial policy.
## Approval
Proposed; CTO approval required.
