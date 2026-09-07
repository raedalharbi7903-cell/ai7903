import pytest

from app.analysis.context import AnalysisContext
from app.analysis.engines import CorrelationEngine, MultiTimeframeEngine, RiskEngine
from app.analysis.models import AnalysisInput, MarketData
from tests.analysis.test_pipeline import fixture_input


def test_correlation_uses_benchmark_history() -> None:
    source = fixture_input()
    source.data["candles"].append(
        {
            "timestamp": "2026-01-01T02:00:00Z",
            "open": 11,
            "high": 13,
            "low": 11,
            "close": 12,
            "volume": 130,
        }
    )
    source.metadata["benchmark_candles"] = source.data["candles"]
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    result = CorrelationEngine().analyze(context)
    assert result.data["coefficient"] == pytest.approx(1.0)


def test_multi_timeframe_detects_conflict() -> None:
    source = fixture_input()
    bearish = fixture_input().data
    bearish["timeframe"] = "4h"
    bearish["candles"] = list(reversed(bearish["candles"]))
    source.metadata["timeframes"] = {
        "1h": source.data,
        "4h": bearish,
        "1d": source.data,
    }
    result = MultiTimeframeEngine().analyze(AnalysisContext(source))
    assert result.data["alignment"] == "conflict"


def test_risk_derives_levels_from_structure() -> None:
    source = fixture_input()
    context = AnalysisContext(
        source, market_data=MarketData.model_validate(source.data)
    )
    context.add_output(
        type(
            "Output",
            (),
            {
                "engine_name": "market_structure",
                "data": {"invalidation": 10},
                "evidence": [],
            },
        )()
    )
    result = RiskEngine().analyze(context)
    assert result.data["risk_reward"] == 2.0
