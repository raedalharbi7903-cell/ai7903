from copy import deepcopy
from datetime import UTC, datetime, timedelta

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
                {
                    "timestamp": "2026-01-01T02:00:00Z",
                    "open": 11,
                    "high": 13,
                    "low": 10,
                    "close": 12,
                    "volume": 130,
                },
                {
                    "timestamp": "2026-01-01T03:00:00Z",
                    "open": 12,
                    "high": 14,
                    "low": 11,
                    "close": 13,
                    "volume": 140,
                },
                {
                    "timestamp": "2026-01-01T04:00:00Z",
                    "open": 13,
                    "high": 15,
                    "low": 12,
                    "close": 14,
                    "volume": 150,
                },
            ],
        }
    )


def test_default_pipeline_contains_canonical_components() -> None:
    assert len(default_engines()) == 28


def timeframe_fixtures(data: dict) -> dict:
    """Distinct synthetic frame snapshots, all closed by the same decision time."""
    end = datetime.fromisoformat(
        data["candles"][-1]["timestamp"].replace("Z", "+00:00")
    )
    frames = {}
    for role, timeframe, seconds in (
        ("htf", "4h", 14400),
        ("itf", "1h", 3600),
        ("ltf", "15m", 900),
    ):
        frame = deepcopy(data)
        frame["timeframe"] = timeframe
        for index, candle in enumerate(frame["candles"]):
            candle["timestamp"] = (
                end - timedelta(seconds=seconds * (len(frame["candles"]) - 1 - index))
            ).isoformat()
        frames[role] = frame
    return frames


def test_fixture_pipeline_is_traceable_and_validated() -> None:
    analysis_input = fixture_input()
    analysis_input.data["candles"][2]["high"] = 30
    analysis_input.metadata["timeframes"] = timeframe_fixtures(analysis_input.data)
    result = AnalysisService().analyze(analysis_input)
    assert result.validation == ValidationStatus.PASS
    assert result.decision == DecisionState.BUY
    assert len(result.outputs) == 28
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
