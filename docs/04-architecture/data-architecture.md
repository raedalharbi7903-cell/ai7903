---
title: Data Architecture
document_id: DOC-04-DATA_ARCHITECTURE-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-08-16
next_review: 2026-11-16
related_documents: [DOC-MANIFEST-001]
---

# Data Architecture

## Purpose

Describe normalized market-data responsibilities and MVP implementation status.

## Scope

Provider abstraction, normalized OHLCV, provenance, validation, and licensing boundaries.

## Main Content

The active validation market is Crypto only. The MVP implements a provider interface, a Twelve Data adapter, and an OKX development/test adapter for crypto OHLCV. Analysis engines consume normalized data only; provider-specific payloads do not cross the adapter boundary. Normalized data retains instrument, market, exchange, asset type, timeframe, OHLCV, provider, timestamps, fixture/live distinction, and quality status.

Duplicate timestamps, invalid OHLC relationships, impossible prices, and future source timestamps are detected. OKX is **DEVELOPMENT / TEST ONLY**: its current API terms restrict market data to personal, non-commercial use and prohibit redistribution, commercial analytics platforms, and commercial AI/ML evaluation absent written permission. Commercial display or redistribution is **LICENSE REQUIRED**; public API access alone does not confer rights. US equities, Saudi equities, and forex are future markets. Freshness/gap thresholds remain **CALIBRATION REQUIRED**.

## Related Documents

[Project Manifest](../01-project/project-manifest.md), [Analysis Pipeline](analysis-pipeline.md)

## Change History

- 1.1.0 - Recorded MVP provider integration and licensing boundary.
- 1.0.0 - Initial proposed specification.

## Approval

Proposed; CTO approval required.
