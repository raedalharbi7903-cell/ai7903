import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
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
    assert response.json()["decision"] == "no_trade"
    assert response.json()["validation"] == "fail"
    risk = next(o for o in response.json()["outputs"] if o["engine_name"] == "risk")
    assert "risk/reward" in risk["warnings"][0]
    findings = response.json()["advanced_findings"]
    assert {item["engine_id"] for item in findings} >= {"candlestick"}
    assert all("details" in item and "warnings" in item for item in findings)


def test_analysis_api_does_not_fabricate_live_data() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analysis", json={"pair": "TEST-USDT", "timeframe": "1h"}
        )
    assert response.status_code == 503


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("fixture", False),
        ("provider", ""),
        ("asset_type", "futures"),
        ("market", "equities"),
        ("instrument", "OTHER-USDT"),
        ("timeframe", "4h"),
    ],
)
def test_invalid_fixture_provenance_is_rejected(key, value) -> None:
    request = payload()
    request["market_data"][key] = value
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=request)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("pair", "BTC/USDT"),
        ("timeframe", "7fortnights"),
    ],
)
def test_invalid_request_dimensions(key, value) -> None:
    request = payload()
    request[key] = value
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=request)
    assert response.status_code == 422


def test_api_rejects_invalid_or_weakened_safety_configuration() -> None:
    with TestClient(app) as client:
        for configuration in (
            {"engine_configuration": {"momentum_divergence": {"right_window": 0}}},
            {"minimum_risk_reward": 0.1},
            {"minimum_stop_atr_multiple": 0},
        ):
            request = payload()
            request["metadata"] = configuration
            response = client.post("/api/v1/analysis", json=request)
            assert response.status_code == 422
            assert "traceback" not in response.text.lower()


def test_schema_is_published_and_advanced_findings_serialize() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        result = client.post("/api/v1/analysis", json=payload()).json()
    assert "/api/v1/analysis" in schema["paths"]
    assert len(result["advanced_findings"]) == 5
    assert all("family" in finding for finding in result["advanced_findings"])
    confidence = next(o for o in result["outputs"] if o["engine_name"] == "confidence")
    assert confidence["data"]["calibration"] == "uncalibrated"


def test_validation_error_does_not_echo_submitted_data() -> None:
    request = payload()
    request["unknown_secret"] = "do-not-reflect-this"
    with TestClient(app) as client:
        response = client.post("/api/v1/analysis", json=request)
    assert response.status_code == 422
    assert "do-not-reflect-this" not in response.text


def test_demo_endpoint_is_disabled_in_production_without_access_controls() -> None:
    production = get_settings().model_copy(update={"environment": "production"})
    app.dependency_overrides[get_settings] = lambda: production
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/analysis", json=payload())
        assert response.status_code == 503
        assert "access controls" in response.json()["error"]["message"]
    finally:
        app.dependency_overrides.pop(get_settings)
