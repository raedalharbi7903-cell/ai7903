from fastapi.testclient import TestClient

from app.main import app
from tests.analysis.test_pipeline import fixture_input


def payload() -> dict[str, object]:
    source = fixture_input()
    source.data["instrument"] = "TEST-USDT"
    source.metadata["timeframes"] = {
        "htf": source.data,
        "itf": source.data,
        "ltf": source.data,
    }
    return {
        "pair": "TEST-USDT",
        "timeframe": "1h",
        "request_id": "api-fixture-1",
        "market_data": source.data,
        "metadata": source.metadata,
    }


def test_fixture_analysis_api_uses_production_service() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=payload())
    assert response.status_code == 200
    assert response.json()["decision"] == "buy"
    assert response.json()["validation"] == "pass"


def test_analysis_api_does_not_fabricate_live_data() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analysis", json={"pair": "TEST-USDT", "timeframe": "1h"}
        )
    assert response.status_code == 503
