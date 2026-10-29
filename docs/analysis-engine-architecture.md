# Analysis Engine Architecture

Sprint 3 defines a framework for future analysis engines without implementing analysis behavior.

Each engine implements the `AnalysisEngine` contract and receives one shared `AnalysisContext`. Engines return a standard `EngineOutput`; the pipeline appends each output to the context before invoking the next engine. `AnalysisPipeline` returns the aggregate `AnalysisResult` after sequential execution.

`EngineRegistry` is explicit and in-memory. Future composition code can register approved engine instances and create a pipeline from their ordered collection. The lifecycle statuses are `pending`, `running`, `completed`, and `failed`; this sprint defines the contract only and does not perform analysis, calculations, recommendations, or market interpretation.

## Runtime implementation update — 2026-10-29

The Sprint 3 description above is historical. The current sequential service has
28 components, including four advanced extensions sharing existing evidence
families. Runtime code lives in backend/app/analysis; tests live in backend/tests/analysis.

Confirmed divergence uses close swings and one-period close differences, not RSI.
Both pivot sets must be confirmed. Matching waits for the full alignment tolerance
plus the right confirmation window, uses unique momentum pivots, and reports
timestamps and confirmation timestamps. Settings are validated and effective.
Defaults are provisional engineering values, not empirically calibrated parameters.

Structure breaks use confirmed high/low swing references and at least two closed
confirmations; a break is emitted once per reference. Sweep labels describe OHLCV
inference only; later closed-candle rejection distinguishes confirmation from a
potential sweep. Volume baseline excludes the current bar; missing, negative,
nonfinite and zero-baseline cases do not become ordinary observations.
Engulfing requires both body boundaries; conflicting candle geometry is neutral.

Closed-prefix analysis stops at the first incomplete candle. Same-family
contradictions affect confluence even for non-independent findings. A failed
required engine or invalid risk prevents actionability; explanation uses the final
validated decision. See PROJECT_SPEC.md at repository root for remaining gaps.
