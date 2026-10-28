from app.analysis.models import AnalysisInput
from app.analysis.service import AnalysisService


def input_with_prefix(size: int) -> AnalysisInput:
    candles = [
        {
            "timestamp": f"2026-01-01T{index:02d}:00:00Z",
            "open": 100 + index,
            "high": 102 + index,
            "low": 99 + index,
            "close": 101 + index,
            "volume": 100 if index < size - 1 else 250,
        }
        for index in range(size)
    ]
    data = {
        "instrument": "TEST-USDT",
        "market": "crypto",
        "timeframe": "1h",
        "provider": "historical_fixture",
        "source_timestamp": candles[-1]["timestamp"],
        "fixture": True,
        "candles": candles,
    }
    return AnalysisInput(
        data=data,
        metadata={"timeframes": {name: data for name in ("htf", "itf", "ltf")}},
    )


def test_advanced_engines_are_reachable_through_analysis_service() -> None:
    result = AnalysisService().analyze(input_with_prefix(8))
    outputs = {output.engine_name: output for output in result.outputs}
    assert {
        "momentum_divergence",
        "liquidity_sweep",
        "market_transition",
        "volume_anomaly",
    } <= set(outputs)
    assert outputs["momentum_divergence"].engine_name == "momentum_divergence"
    assert outputs["liquidity_sweep"].engine_name == "liquidity_sweep"
    assert outputs["market_transition"].engine_name == "market_transition"
    assert outputs["volume_anomaly"].engine_name == "volume_anomaly"


def test_advanced_analysis_uses_only_available_historical_prefix() -> None:
    prefix = AnalysisService().analyze(input_with_prefix(7))
    extended = AnalysisService().analyze(input_with_prefix(8))
    prefix_divergence = next(
        output
        for output in prefix.outputs
        if output.engine_name == "momentum_divergence"
    )
    extended_divergence = next(
        output
        for output in extended.outputs
        if output.engine_name == "momentum_divergence"
    )
    assert prefix_divergence.data["sample_size"] == 7
    assert extended_divergence.data.get("confirmation_windows") == {
        "left": 1,
        "right": 1,
    }
