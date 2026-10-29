---
title: Request Isolation Acceptance
document_id: DOC-TEST-ISOLATION-001
version: 1.0.0
status: verified-limited-scope
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-29
related_documents: [DOC-ARCH-PIPELINE-001]
---

# Request isolation acceptance

## Purpose

Record reproducible request-state and fixture security acceptance without claiming
production capacity, authentication, tenant isolation or a completed penetration test.

## Scope

The default AnalysisService, FastAPI fixture endpoint and typed frontend client.
Tests use synthetic observations only and execute the actual service/pipeline.

## Main content

The initial mutation probe failed: an injected engine could change nested metadata
and candle values in caller-owned AnalysisInput. AnalysisService now creates a
deep request-owned snapshot before constructing its shared context. Engines still
share that context within one run; the architecture and public contract are unchanged.

| Scenario | Evidence | Verified property |
| --- | --- | --- |
| Mutating engine | backend/tests/analysis/test_request_isolation.py | Original caller input unchanged |
| 64 calls / 8 workers, one service | Same test module | Decisions, failures and instrument evidence stay request-local |
| 32 calls / 8 workers, FastAPI TestClient | backend/tests/api/test_security_acceptance.py | Distinct fixture instruments/provenance preserved; live provider and external GET hooks never invoked |
| Negative OHLCV and oversized fixture | Same API test module | Structured 422 rejection |
| 16 concurrent real HTTP calls | frontend/src/features/analysis/analysis.integration.test.tsx | Typed client reaches actual Uvicorn/FastAPI; fixture identity, advanced output and uncalibrated status preserved |

No timing threshold is invented. These bounded workloads are regression acceptance,
not sustained load, production throughput, memory exhaustion, distributed isolation,
security certification or multi-worker deployment acceptance. Missing MTF fixtures
in the real-HTTP case cannot become executable BUY/SELL results.

## Related documents

- [Runtime resilience](runtime-resilience-results.md)
- [Requirement evidence matrix](requirement-evidence-matrix.md)
- [Analysis pipeline](../04-architecture/analysis-pipeline.md)

## Change history

- 1.0.0 — Recorded mutation defect, snapshot correction and bounded concurrency scope.
