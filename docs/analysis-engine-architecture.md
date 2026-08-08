# Analysis Engine Architecture

Sprint 3 defines a framework for future analysis engines without implementing analysis behavior.

Each engine implements the `AnalysisEngine` contract and receives one shared `AnalysisContext`. Engines return a standard `EngineOutput`; the pipeline appends each output to the context before invoking the next engine. `AnalysisPipeline` returns the aggregate `AnalysisResult` after sequential execution.

`EngineRegistry` is explicit and in-memory. Future composition code can register approved engine instances and create a pipeline from their ordered collection. The lifecycle statuses are `pending`, `running`, `completed`, and `failed`; this sprint defines the contract only and does not perform analysis, calculations, recommendations, or market interpretation.
