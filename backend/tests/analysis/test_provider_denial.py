"""No dormant adapter or vendor default can authorize live data access."""

from unittest.mock import patch

import pytest

from app.analysis.data_contracts import DataAcquisitionError
from app.analysis.providers import OkxProvider
from app.config.settings import Settings


@pytest.mark.parametrize(
    "environment", ["development", "testing", "staging", "production"]
)
def test_no_provider_or_endpoint_is_implicitly_selected(monkeypatch, environment):
    monkeypatch.delenv("MARKET_DATA_PROVIDER", raising=False)
    monkeypatch.delenv("MARKET_DATA_BASE_URL", raising=False)
    settings = Settings(
        _env_file=None,
        APP_NAME="synthetic-config-test",
        APP_ENVIRONMENT=environment,
        LOG_LEVEL="WARNING",
        DATABASE_URL="sqlite://",
    )
    assert settings.market_data_provider is None
    assert settings.market_data_base_url is None


@pytest.mark.parametrize("timeframe", ["1h", "4h", "1d"])
def test_direct_legacy_provider_denies_before_any_network(timeframe, monkeypatch):
    monkeypatch.setenv("MARKET_DATA_PROVIDER", "okx")
    monkeypatch.setenv("MARKET_DATA_API_KEY", "synthetic-not-a-real-secret")
    monkeypatch.setenv("MARKET_DATA_BASE_URL", "https://unapproved.invalid")
    with patch("httpx.get", side_effect=AssertionError("No external call")) as fetch:
        with pytest.raises(DataAcquisitionError) as caught:
            OkxProvider().candles("TEST-USDT", timeframe)
    assert caught.value.category == "live_access_unapproved"
    fetch.assert_not_called()
