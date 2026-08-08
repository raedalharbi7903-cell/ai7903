---
title: Decision Hierarchy
document_id: DOC-DECISION-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-08
next_review: 2026-11-08
related_documents: [DOC-ENGINEERING-001, DOC-MANIFEST-001]
---

# Decision Hierarchy

## Purpose

Define authority and escalation for project decisions.

## Scope

Applies to implementation and governance work.

## Main Content

Green decisions are autonomous: non-breaking fixes, tests, linting, documentation, cleanup, performance work without behavior change, and internal improvements.

Yellow decisions may be implemented and must be reported: folder organization, internal abstractions, minor configuration, and developer-experience improvements.

Red decisions require CTO approval before implementation: Manifest or Handbook changes, architecture baseline changes, AI philosophy changes, decision-engine behavior, analysis-engine additions or removals, API contract changes, breaking changes, major dependencies, redesigns, and product strategy.

When a red decision is blocked, report options, trade-offs, and a recommendation.

## Related Documents

[Engineering Philosophy](engineering-philosophy.md), [Project Manifest](project-manifest.md)

## Change History

- 1.0.0 — Initial approval hierarchy.
