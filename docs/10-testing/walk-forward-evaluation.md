---
title: Fixed-Parameter Walk-Forward Evaluation
document_id: DOC-WALK-FORWARD-001
version: 1.0.0
status: synthetic-framework-empirical-acceptance-open
owner: Engineering
reviewers: Founder
last_updated: 2026-10-31
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Walk-forward evaluation

## Purpose

Execute chronological test folds through the existing HistoricalBacktester and
AnalysisService without including training/warmup returns in test metrics.

## Scope

Fixed parameters and synthetic verification only. No fitting/optimization, new
trading simulator, probability calibration, empirical profitability threshold or
licensed dataset is introduced.

## Main content

WalkForwardConfig explicitly supplies training_size (at least3), test_size
(at least2), expanding/rolling window, positional gap_size (default0) and
include_partial (defaultfalse). Booleans and invalid integer bounds are rejected.
build_folds constructs half-open, nonoverlapping chronological test windows.
Incomplete trailing folds are excluded unless explicitly requested and viable.

The last test candle is outcome-only. Decision bounds restrict the existing
backtester so both the decision and its outcome lie inside the test fold.
Training and gap returns never enter fold metrics. The optional existing
run_pipeline decision_start_index/decision_end_index are internal additive
bounds; their default preserves previous evaluation behavior.

The positional gap excludes observations from the declared training range, but
those historical candles remain legitimately visible at later decision times.
This is NOT label-horizon purging/embargo. No training algorithm runs:
training_performed is false. Do not describe these results as fitted out-of-sample
model performance.

Rolling versus expanding changes the declared warmup/provenance range, not the
existing analytical algorithms' lookback. The evaluator still supplies the complete
available past prefix; it does not silently retrain or truncate those algorithms.

WalkForwardEvaluator receives explicit dataset_id/content_version, execution costs/
assumptions, primary candles and optional auxiliary timeframes. It copies input,
uses only the fold's available primary prefix and existing point-in-time auxiliary
selection. Reports include fold indices/timestamps, decision/outcome times,
prefix-scoped primary/auxiliary fingerprints and the original bounded evaluator
results. Same inputs/configuration produce the same report. Future append cannot
rewrite completed earlier folds.

Existing constraints remain: spot-long bounded evaluation, fees/slippage/stop/gap
assumptions explicitly represented, SELL not short execution, unsafe risk excluded.
Telemetry failure remains isolated. This is not a portfolio accounting engine.

### Verification and unresolved policy

48 new tests in backend/tests/analysis/test_walk_forward.py cover bounds, actual
service invocation, no training/gap returns, auxiliary/primary no-lookahead,
prefix invariance, partial folds, nonmutation, reproducibility and telemetry failure.
Existing backtesting/historical/calibration tests also pass in focused verification.

Decision Required: empirical objectives/acceptance, independent licensed datasets,
fitting/parameter-selection protocol, regime definitions, uncertainty statistics
and label-horizon purging if later applicable. No assumed percentage accuracy,
profitability or calibrated confidence results are published.

## Related documents

- [Historical safety methodology](../05-analysis/legacy-methodology-review.md)
- [Canonical requirements](../02-product/canonical-requirements.json)
- [Gap register](../handover/REMAINING_WORK.md)

## Change history

- 1.0.0 — Fixed-parameter chronological evaluation and explicit test bounds.
