from app.analysis.context import AnalysisContext
from app.analysis.engines import default_engines
from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.pipeline import AnalysisPipeline


class AnalysisService:
    def analyze(self, analysis_input: AnalysisInput) -> AnalysisResult:
        return AnalysisPipeline(default_engines()).run(AnalysisContext(analysis_input))
