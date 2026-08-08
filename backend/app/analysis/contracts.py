from typing import Protocol

from app.analysis.context import AnalysisContext
from app.analysis.models import EngineOutput


class AnalysisEngine(Protocol):
    """Contract implemented by every analysis engine."""

    @property
    def name(self) -> str: ...

    def execute(self, context: AnalysisContext) -> EngineOutput: ...
