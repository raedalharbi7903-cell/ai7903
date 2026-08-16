from datetime import UTC, datetime

from app.analysis.engines import default_engines
from app.analysis.models import AnalysisInput, DecisionState, ValidationStatus
from app.analysis.service import AnalysisService


def fixture_input() -> AnalysisInput:
    return AnalysisInput(
        data={
            "instrument": "TEST",
            "market": "fixture",
            "timeframe": "1h",
            "provider": "test-fixture",
            "source_timestamp": datetime.now(UTC).isoformat(),
            "fixture": True,
            "candles": [
                {
                    "timestamp": "2026-01-01T00:00:00Z",
                    "open": 10,
                    "high": 11,
                    "low": 9,
                    "close": 10,
                    "volume": 100,
                },
                {
                    "timestamp": "2026-01-01T01:00:00Z",
                    "open": 10,
                    "high": 12,
                    "low": 10,
                    "close": 11,
                    "volume": 120,
                },
            ],
        }
    )


def test_default_pipeline_contains_canonical_components() -> None:
    assert len(default_engines()) == 24


def test_fixture_pipeline_is_traceable_and_validated() -> None:
    result = AnalysisService().analyze(fixture_input())
    assert result.validation == ValidationStatus.PASS
    assert result.decision == DecisionState.BUY
    assert len(result.outputs) == 24
    assert any(output.evidence for output in result.outputs)


def test_missing_data_returns_insufficient_data_without_fabrication() -> None:
    result = AnalysisService().analyze(AnalysisInput())
    assert result.validation == ValidationStatus.FAIL
    assert result.decision == DecisionState.INSUFFICIENT_DATA


def test_ai_unavailable_does_not_block_deterministic_result() -> None:
    result = AnalysisService().analyze(fixture_input())
    ai_output = next(
        output for output in result.outputs if output.engine_name == "ai_reasoning"
    )
    assert ai_output.status.value == "degraded"
    assert ai_output.data["available"] is False
