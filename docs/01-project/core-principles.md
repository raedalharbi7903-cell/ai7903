---
title: Core Principles
document_id: DOC-CORE-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-08
next_review: 2026-11-08
related_documents: [DOC-MANIFEST-001, DOC-ENGINEERING-001]
---

# Core Principles

## Purpose

Provide concise, non-negotiable principles for project decisions.

## Scope

Applies across engineering and product delivery.

## Main Content

1. Readable code first.
2. One responsibility per module.
3. No hidden behavior or duplicated logic.
4. Business logic does not belong in routes.
5. Configuration, secrets, and connection strings come from environment variables.
6. Deterministic analysis precedes AI explanation.
7. Validate, report, and fix before review.
8. Preserve compatibility unless a breaking change is approved.
9. Document material decisions near the time they are made.

## Related Documents

[Project Manifest](project-manifest.md), [Engineering Philosophy](engineering-philosophy.md)

## Change History

- 1.0.0 — Initial core principles.
