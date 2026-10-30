---
title: Provider-Neutral Acquisition Foundation
document_id: DOC-DATA-ACQUISITION-001
version: 1.0.0
status: implemented-foundation-product-incomplete
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Provider-neutral acquisition

## Purpose

Implement safe acquisition contracts without choosing or calling an unapproved provider.

## Scope

Requirement group MASTER-11; DATA-CONTRACT, DATA-RETRY and DATA-CACHE.
This is a fixture contract environment, not licensed live ingestion or a new public API.

## Main content

MarketDataRequest in backend/app/analysis/data_contracts.py is strict/frozen:
crypto pair, supported timeframe, aware as-of, limit and minimum coverage.
The trusted MarketDataProvider protocol exposes provider identity, fixture/live
mode and fetch. Adapters own bounded I/O timeouts; no adapter is selected by default.

MarketDataService defaults disabled. It rejects every live adapter before fetch,
even when fixture mode is explicitly enabled. Enabling fixtures is not a licensing
grant. Production/API behavior remains unchanged and demo analysis stays disabled
in production. The existing development OKX adapter was not wired into this service.

Returned snapshots are revalidated and deep-copied. Identity, timeframe, crypto
market, fixture provenance, closed observations, UTC normalization, finite OHLCV,
nonfuture source/candle timestamps, source-after-observation consistency, ordered
cadence, coverage and freshness are enforced. Missing volume is preserved, not
fabricated; downstream engines retain their insufficient-evidence handling.

Only TransientProviderError is retried. Default: at most three attempts,
0.1-second exponential backoff capped at two seconds. Operational configuration
bounds attempts to five and delay to ten seconds. Retry-After above the configured
maximum causes safe failure rather than retrying too soon. Permanent/invalid errors
are not retried. Consumers receive bounded categories, never raw provider messages.
These bounds are operational defaults, not calibrated analytical thresholds.

Optional caching is disabled by default. When explicitly enabled, a private
service/provider-instance cache uses complete immutable requests including as-of,
timeframe, pair, limit and required coverage. Default 32 entries/30-second TTL;
hard resource bounds 128 entries/300 seconds. LRU operations are locked and both
ingress/egress are deep-copied. Provider identity/mode guards run before cache lookup.
This is not a distributed cache or a live-data revision policy.

MarketDataService.analyze sends validated data into the existing AnalysisService
with the explicit decision timestamp. It does not create a second analysis pipeline.
Tests verify all 28 outputs and evidence provider provenance through that actual path.
Independent MTF inputs are not synthesized or copied from the primary series.

Tests: backend/tests/analysis/test_data_acquisition.py and test_data_cache.py.
Shared model coercion regressions in test_boolean_boundaries.py reject boolean
OHLCV and non-boolean complete/fixture flags before they can falsify price,
closed-candle or provenance semantics. Valid integers/floats and optional missing
volume remain accepted. Raw invalid inputs fail closed through AnalysisService.
They use synthetic in-process adapters, deterministic clocks/waits and zero network
or licensed data. Retry/caching tests are not real-provider SLA acceptance.

Remaining: reviewed commercial rights/access/adapter, HTTP status/Retry-After parsing,
actual rate limits, ingestion persistence, licensed historical coverage/revisions,
measured request/resource-cost telemetry and real provider failure acceptance.
No financial cost figures or real data quality claims are invented.

## Related documents

- [Master directive](../02-product/approved-master-execution-goal.md)
- [Canonical requirements](../02-product/canonical-requirements.json)
- [Data architecture](../04-architecture/data-architecture.md)
- [External dependency register](../handover/REMAINING_WORK.md)

## Change history

- 1.0.0 — Added validated fixture acquisition, bounded retry and isolated cache into the existing service.
