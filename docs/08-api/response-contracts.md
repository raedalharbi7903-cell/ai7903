---
title: Response Contracts
document_id: DOC-08-RESPONSE_CONTRACTS-001
version: 1.0.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-11
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Response Contracts
## Purpose
Define standards for Response Contracts.
## Scope
Architecture and governance specification only; no runtime behavior is implemented by this document.
## Main Content
This document records the approved boundary for Response Contracts. Current implementation is limited to documented foundations; specific providers, legal claims, permissions, formulas, infrastructure, and operational thresholds are Decision Required. Future work must preserve explicit validation, traceability, security, and approval boundaries.

**Implemented:** documentation only. **Approved Future Architecture:** this subject may be implemented only through approved work. **Decision Required:** exact algorithms, formulas, providers, permissions, and operational thresholds are not approved unless stated otherwise.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.0.0 — Initial proposed specification.
## Approval
Proposed; CTO approval required.

## Implemented fixture contract — 2026-10-29

POST /api/v1/analysis accepts a pair, supported timeframe, optional request_id,
typed market_data and typed metadata. Pair/timeframe must match provenance.
Only explicitly labeled cryptocurrency/fixture spot data is accepted; invalid
numerical data, unknown settings and risk-bound weakening return structured 422
errors. Missing data returns 503 rather than invoking an unapproved provider.
Production environment disables this unauthenticated demo endpoint with 503.

AnalysisResult declares contract_version 1.0, lifecycle status, decision,
validation, generated_at, engine outputs and advanced_findings. Advanced findings
include engine_id, status, family, classification, direction, details, provenance
and warnings. Additive fields preserve the existing versioned endpoint. Decisions
are buy, sell, no_trade, wait, insufficient_data. Confidence remains uncalibrated
analytical quality, never probability of profit. The frontend runtime-checks this
contract and hides risk levels when final validation is not actionable.

OpenAPI is generated from app/schemas/analysis.py and app/analysis/models.py.
Validation errors contain locations/types/messages, not submitted input values.
Authentication and approved production access controls remain incomplete.
