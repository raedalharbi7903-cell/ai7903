from datetime import datetime

from app.analysis.models import AnalysisInput
from app.analysis.service import AnalysisService
from tests.analysis.test_decision_states import complete_input


def test_historical_evidence_is_timestamped_to_observations_not_wall_clock() -> None:
    source = complete_input()
    result = AnalysisService().analyze(source)
    observed = datetime.fromisoformat(
        source.data["candles"][-1]["timestamp"].replace("Z", "+00:00")
    )
    evidence = [item for output in result.outputs for item in output.evidence]
    assert evidence
    for item in evidence:
        assert item.timestamp == observed
        assert item.provenance["observed_at"] == observed.isoformat()
        assert item.provenance["provider"] == source.data["provider"]
        assert item.provenance["fixture"] == "True"
    assert result.generated_at > observed


def test_replaying_prefix_preserves_evidence_time_and_findings() -> None:
    source = complete_input()
    first = AnalysisService().analyze(source)
    second = AnalysisService().analyze(
        AnalysisInput.model_validate(source.model_dump())
    )

    def observations(result):
        return [
            (item.source_engine, item.timestamp, item.finding, item.provenance)
            for output in result.outputs
            for item in output.evidence
        ]

    assert observations(first) == observations(second)
