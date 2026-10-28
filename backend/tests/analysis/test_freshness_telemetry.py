from datetime import UTC, datetime, timedelta

from app.analysis.freshness import FreshnessPolicy, assess_market_data
from app.analysis.models import Candle, FreshnessStatus, MarketData
from app.analysis.service import AnalysisService
from app.analysis.telemetry import InMemoryTelemetrySink
from tests.analysis.test_pipeline import fixture_input


def market_data(last_timestamp: datetime, complete: bool = True) -> MarketData:
    return MarketData(
        instrument="TEST",
        market="crypto",
        timeframe="1h",
        provider="fixture-provider",
        source_timestamp=last_timestamp,
        fixture=True,
        candles=[
            Candle(
                timestamp=last_timestamp - timedelta(hours=1),
                open=10,
                high=11,
                low=9,
                close=10,
            ),
            Candle(
                timestamp=last_timestamp,
                open=10,
                high=12,
                low=10,
                close=11,
                complete=complete,
            ),
        ],
    )


def test_freshness_distinguishes_fresh_delayed_stale_and_incomplete() -> None:
    reference = datetime(2026, 1, 2, tzinfo=UTC)
    policy = FreshnessPolicy(delayed_after_intervals=1, stale_after_intervals=3)
    assert (
        assess_market_data(market_data(reference), reference, policy).status
        == FreshnessStatus.FRESH
    )
    assert (
        assess_market_data(
            market_data(reference - timedelta(hours=2)), reference, policy
        ).status
        == FreshnessStatus.DELAYED
    )
    assert (
        assess_market_data(
            market_data(reference - timedelta(hours=4)), reference, policy
        ).status
        == FreshnessStatus.STALE
    )
    assert (
        assess_market_data(
            market_data(reference, complete=False), reference, policy
        ).reason
        == "incomplete_latest_candle"
    )


def test_analysis_telemetry_is_structured_and_failure_isolated() -> None:
    sink = InMemoryTelemetrySink()
    source = fixture_input()
    source.metadata["request_id"] = "analysis-42"
    AnalysisService(sink).analyze(source)
    event = sink.events[0]
    assert event.request_id == "analysis-42"
    assert event.provider == "test-fixture"
    assert event.duration_ms >= 0


def test_telemetry_sink_failure_does_not_break_analysis() -> None:
    class BrokenSink:
        def record_analysis(self, event: object) -> None:
            raise RuntimeError("telemetry unavailable")

    result = AnalysisService(BrokenSink()).analyze(fixture_input())
    assert result.decision.value in {"buy", "no_trade"}


def test_stale_primary_data_prevents_executable_decision() -> None:
    source = fixture_input()
    source.metadata["decision_timestamp"] = "2026-01-01T09:00:00Z"
    source.metadata["timeframes"] = {
        "htf": source.data,
        "itf": source.data,
        "ltf": source.data,
    }
    result = AnalysisService().analyze(source)
    assert result.decision.value == "no_trade"
    assert result.validation.value == "fail"
