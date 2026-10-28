---
title: Observability Standards
document_id: DOC-ENG-OBS-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-28
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Observability Standards
## Purpose
Define observability expectations.
## Scope
Lightweight in-process analysis telemetry for Command Center readiness; no dashboard or external telemetry infrastructure.
## Main Content
`AnalysisService` accepts an optional telemetry sink and emits a structured analysis event with request identifier, execution status/duration, provider, quality, freshness, MTF state, independent evidence-family count, decision, validation outcome, confidence state, and risk warning category. Engine timing is retained in the request context for an in-process consumer. Telemetry is deliberately isolated: sink failures never invalidate analysis.

Events do not include credentials, raw request metadata, account data, or unbounded raw market payloads. The in-memory sink exists only for tests and local development. Persistence, retention, metrics export, alerts, resource-cost accounting, Command Center UI, and backtest event schema remain Decision Required.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
- 1.1.0 — Documented implemented safe telemetry hook boundary.
## Approval
Proposed; CTO approval required.
