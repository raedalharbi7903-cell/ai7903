from dataclasses import dataclass, field

from app.analysis.models import AnalysisInput, EngineOutput


@dataclass
class AnalysisContext:
    """Shared execution state passed sequentially between engines."""

    analysis_input: AnalysisInput
    outputs: list[EngineOutput] = field(default_factory=list)

    def add_output(self, output: EngineOutput) -> None:
        self.outputs.append(output)
