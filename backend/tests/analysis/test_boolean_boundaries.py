"""Reject coercion that can falsify price, closed-candle or fixture semantics."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.analysis.models import Candle, MarketData
from app.analysis.service import AnalysisService
from tests.analysis.test_pipeline import fixture_input


def candle(**changes):
    return Candle(
        **dict(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.2,
            volume=100,
        )
        | changes
    )


@pytest.mark.parametrize("field", ["open", "high", "low", "close", "volume"])
@pytest.mark.parametrize("value", [True, False])
def test_boolean_observations_are_not_numeric_prices_or_volume(field, value):
    with pytest.raises(ValidationError):
        candle(**{field: value})


@pytest.mark.parametrize("value", ["true", "false", 1, 0])
def test_closed_status_is_not_inferred_from_non_boolean_flags(value):
    with pytest.raises(ValidationError):
        candle(complete=value)


@pytest.mark.parametrize("value", ["true", "false", 1, 0])
def test_fixture_provenance_is_not_coerced(value):
    with pytest.raises(ValidationError):
        MarketData.model_validate({**fixture_input().data, "fixture": value})


def test_genuine_boolean_flags_and_numeric_observations_remain_supported():
    observed = candle(open=1, complete=False, volume=None)
    assert observed.open == 1.0
    assert observed.complete is False
    assert observed.volume is None


def test_internal_raw_payload_boolean_price_cannot_pass_the_production_pipeline():
    payload = fixture_input()
    for row in payload.data["candles"]:
        row.update(open=True, high=2.0, low=0.5, close=1.2)
    result = AnalysisService().analyze(payload)
    data = next(output for output in result.outputs if output.engine_name == "data")
    assert data.status == "failed"
    assert result.decision == "insufficient_data"
