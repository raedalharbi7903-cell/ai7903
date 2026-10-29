from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.analysis.test_decision_states import complete_input
from tests.api.test_analysis import payload


def test_parallel_api_requests_do_not_mix_instruments_or_acquire_live_data() -> None:
    def request(index):
        source = complete_input()
        pair = f"FIXTURE{index}-USDT"
        source.data["instrument"] = pair
        for frame in source.metadata["timeframes"].values():
            frame["instrument"] = pair
        response = client.post(
            "/api/v1/analysis",
            json={
                "pair": pair,
                "timeframe": "1h",
                "market_data": source.data,
                "metadata": source.metadata,
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["decision"] == "buy"
        assert result["validation"] == "pass"
        for output in result["outputs"]:
            for item in output["evidence"]:
                assert item["instrument"] == pair
                assert item["provenance"]["fixture"] == "True"
        return result

    with (
        patch(
            "httpx.get", side_effect=AssertionError("No external GET allowed")
        ) as get,
        patch(
            "app.analysis.providers.OkxProvider.candles",
            side_effect=AssertionError("No live provider allowed"),
        ) as provider,
        TestClient(app) as client,
        ThreadPoolExecutor(max_workers=8) as executor,
    ):
        results = list(executor.map(request, range(32)))
        get.assert_not_called()
        provider.assert_not_called()
    assert len(results) == 32


@pytest.mark.parametrize("field", ["open", "close", "high", "low", "volume"])
def test_negative_candle_observations_are_rejected_at_api_boundary(field) -> None:
    request = payload()
    request["market_data"]["candles"][-1][field] = -1
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=request)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_bounded_fixture_size_is_enforced() -> None:
    request = payload()
    # No fabricated market history; deliberately invalid synthetic request size.
    request["market_data"]["candles"] *= 1001
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=request)
    assert response.status_code == 422
    assert "at most 5000" in response.text
