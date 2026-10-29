# Runtime resilience and synthetic latency evidence

Version 1.0 — 2026-10-29 — Engineering.

## Failure safety

The pipeline records unexpected engine exceptions as failed outputs with sanitized
warnings. Structured logs contain engine identity and exception category, not the
exception message or request body. Other engines still execute for diagnostics;
final reconciliation rejects actionability after any failed component, including
failures occurring after the validation/explanation engines.

Decision, validation output, explanation and telemetry are reconciled to the same
safe result. This is conservative fail-closed behavior, not graceful continuation
of an executable recommendation. AI-provider absence remains its explicitly
degraded state, not a fabricated narrative.

tests/analysis/test_failure_isolation.py injects exceptions at four positions,
including after all ordinary components. tests/api/test_error_boundary.py checks
consistent sanitized 500 responses for unexpected and database exceptions.
test_safety_acceptance.py additionally checks nonfinite, negative, boolean and
malformed volatility observations cannot bypass risk limits.

## Local latency baseline

Run backend/.venv/Scripts/python scripts/benchmark_analysis.py from the repository
root (use .venv/bin/python on Unix). The script measures actual AnalysisService
calls over synthetic data after one excluded warm-up per size, and writes raw
durations and aggregates to .verification/latency-baseline.json.

Observed in this execution, 20 samples per size:

| Candles | p50 ms | p95 ms | Maximum ms |
| --- | --- | --- | --- |
| 32 | 0.549 | 0.772 | 1.206 |
| 256 | 1.586 | 3.498 | 5.724 |
| 1024 | 6.044 | 7.274 | 7.322 |

These are machine-specific warm sequential in-process measurements. The fixture
has no independent MTF inputs, so those components take their unavailable path.
This is not HTTP load testing, concurrent capacity validation, production latency
acceptance, a complete all-engine workload, or a financial result. No production
SLO is asserted. Licensed-data workloads, concurrency, database/network overhead
and deployment-specific resource limits remain unverified.

## Closed-history regression update

Freshness is measured from the last closed observation, not an incomplete tail.
An old closed prefix remains stale even if a recent incomplete observation is
present. No closed observations yields missing data; an incomplete middle candle
or naive decision reference is invalid. Freshness configuration rejects inverted,
negative and noninteger windows.

Classic volume and volume anomaly now share historical-baseline validation.
Missing observations are not removed to make an older sample look current.
Zero baselines remain insufficient rather than a directional contraction.
Flat close history produces neutral RSI 50. Regression evidence is in
backend/tests/analysis/test_freshness_boundaries.py.

## Hosted evidence boundary

GitHub run 40915087207 completed its Docker build and documentation audit, but
failed frontend test startup on Linux. Local Windows verification does not prove
that hosted defect fixed. The subsequent workflow adds native source-map
diagnostics and a container runtime smoke check; execution must be inspected.
Mocked container tests only prove cleanup/denial logic, not a working image.
