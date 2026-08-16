from dataclasses import dataclass, field
from typing import Any

from app.analysis.models import AnalysisInput, EngineOutput, Evidence, MarketData


@dataclass
class AnalysisContext:
    analysis_input: AnalysisInput
    market_data: MarketData | None = None
    outputs: list[EngineOutput] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)

    def add_output(self, output: EngineOutput) -> None:
        self.outputs.append(output)
        self.evidence.extend(output.evidence)

    def output(self, name: str) -> EngineOutput | None:
        return next((item for item in self.outputs if item.engine_name == name), None)
