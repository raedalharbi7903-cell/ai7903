from app.analysis.contracts import AnalysisEngine


class EngineRegistry:
    """In-memory registry for explicit engine discovery and registration."""

    def __init__(self) -> None:
        self._engines: dict[str, AnalysisEngine] = {}

    def register(self, engine: AnalysisEngine) -> None:
        if engine.name in self._engines:
            raise ValueError(f"Engine '{engine.name}' is already registered")
        self._engines[engine.name] = engine

    def get(self, name: str) -> AnalysisEngine:
        return self._engines[name]

    def all(self) -> tuple[AnalysisEngine, ...]:
        return tuple(self._engines.values())
