from app.analysis.models import MarketData, ValidationStatus
from app.analysis.providers import validate_market_data
from tests.analysis.test_pipeline import fixture_input


def test_fixture_market_data_is_valid() -> None:
    data = MarketData.model_validate(fixture_input().data)
    assert validate_market_data(data) is ValidationStatus.PASS


def test_duplicate_candles_are_invalid() -> None:
    payload = fixture_input().data
    payload["candles"].append(payload["candles"][0])
    data = MarketData.model_validate(payload)
    assert validate_market_data(data) is ValidationStatus.FAIL
