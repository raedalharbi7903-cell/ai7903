from math import isfinite

import pytest

from app.analysis.deterministic import atr, correlation, rsi, sma
from app.analysis.engines import BaseEngine, default_engines
from app.analysis.models import EngineLifecycleStatus, EngineOutput
from app.analysis.service import AnalysisService
from tests.analysis.test_decision_states import complete_input
from tests.analysis.test_deterministic import candles


@pytest.mark.parametrize("period", [0, -1, True, 1.5])
@pytest.mark.parametrize("function", [sma, rsi])
def test_invalid_periods_are_rejected(function, period) -> None:
    with pytest.raises(ValueError):
        function([1, 2, 3], period)


@pytest.mark.parametrize("period", [0, -1, True, 1.5])
def test_atr_rejects_invalid_periods(period) -> None:
    with pytest.raises(ValueError):
        atr(candles(), period)


def test_large_finite_average_does_not_overflow() -> None:
    assert sma([1e308] * 5, 5) == pytest.approx(1e308)
    assert isfinite(sma([1e308] * 5, 5))


def test_large_finite_rsi_is_not_nan() -> None:
    values = [1e308 if index % 2 else 1 for index in range(15)]
    assert rsi(values) == pytest.approx(50)


def test_large_and_tiny_correlations_are_scale_invariant() -> None:
    for scale in (1e307, 1e-307):
        first = [scale, 2 * scale, 3 * scale]
        assert correlation(first, first) == pytest.approx(1)
        assert correlation(first, first[::-1]) == pytest.approx(-1)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_numeric_observations_are_rejected(invalid) -> None:
    with pytest.raises(ValueError):
        sma([1, invalid, 3], 3)
    with pytest.raises(ValueError):
        rsi([1, invalid, 3], 2)
    with pytest.raises(ValueError):
        correlation([1, invalid, 3], [1, 2, 3])


def test_existing_arithmetic_window_reference_values_are_preserved() -> None:
    assert sma([1, 3, 2, 4, 3], 3) == 3
    assert rsi([1, 3, 2, 4, 3], 4) == pytest.approx(200 / 3)
    assert atr(candles(), 14) == 3
    assert correlation([1, 2, 3], [2, 1, 2]) == pytest.approx(0)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_engine_output_fails_closed_in_production_service(invalid) -> None:
    class OverflowEngine(BaseEngine):
        name = "overflow-test"

        def analyze(self, context):
            return EngineOutput(
                engine_name=self.name,
                status=EngineLifecycleStatus.COMPLETED,
                data={"nested": [{"measurement": invalid}]},
            )

    result = AnalysisService(engines=(*default_engines(), OverflowEngine())).analyze(
        complete_input()
    )
    assert result.validation.value == "fail"
    assert result.decision.value == "no_trade"
    failed = result.outputs[-1]
    assert failed.status == EngineLifecycleStatus.FAILED
    assert failed.data == {}
