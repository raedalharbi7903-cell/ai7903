"""Requirements: DATA-CONTRACT, DATA-RETRY, DATA-PIPELINE; no real provider calls."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.analysis.data_contracts import (
    DataAcquisitionError,
    MarketDataRequest,
    RetryPolicy,
    TransientProviderError,
)
from app.analysis.models import MarketData
from app.services.market_data import MarketDataService
from tests.analysis.test_pipeline import fixture_input

AS_OF = datetime(2026, 1, 1, 4, tzinfo=UTC)


def request(**changes) -> MarketDataRequest:
    return MarketDataRequest(
        **dict(instrument="TEST-USDT", timeframe="1h", as_of=AS_OF, limit=5) | changes
    )


class FixtureProvider:
    provider_id = "contract-fixture"
    mode = "fixture"

    def __init__(self, failures=()):
        payload = fixture_input().data
        payload.update(
            instrument="TEST-USDT",
            market="crypto",
            provider=self.provider_id,
            source_timestamp=AS_OF,
        )
        self.data = MarketData.model_validate(payload)
        self.failures = list(failures)
        self.calls = 0

    def fetch(self, query):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return self.data


def service(provider=None, **options):
    return MarketDataService(
        provider or FixtureProvider(), fixture_enabled=True, **options
    )


def test_no_provider_is_selected_or_enabled_implicitly() -> None:
    for acquisition in (MarketDataService(), MarketDataService(FixtureProvider())):
        with pytest.raises(DataAcquisitionError, match="provider_unavailable"):
            acquisition.fetch(request())


def test_live_adapter_is_denied_before_any_call_even_in_fixture_environment() -> None:
    provider = FixtureProvider()
    provider.mode = "live"
    with pytest.raises(DataAcquisitionError, match="live_access_unapproved"):
        service(provider).fetch(request())
    assert provider.calls == 0


def test_owned_normalized_snapshot_does_not_mutate_adapter_or_other_requests() -> None:
    provider = FixtureProvider()
    provider.data.source_timestamp = AS_OF.astimezone(timezone(timedelta(hours=3)))
    before = provider.data.model_dump()
    acquisition = service(provider)
    first = acquisition.fetch(request())
    first.candles[0].close = 999
    second = acquisition.fetch(request())
    assert second.candles[0].close == 10
    assert second.source_timestamp.tzinfo is UTC
    assert provider.data.model_dump() == before


@pytest.mark.parametrize(
    "changes",
    [
        {"instrument": "BTCUSDT"},
        {"timeframe": "30m"},
        {"as_of": AS_OF.replace(tzinfo=None)},
        {"limit": True},
        {"limit": 0},
        {"limit": 5001},
        {"minimum_candles": 6},
        {"minimum_candles": "2"},
        {"provider": "unapproved"},
    ],
)
def test_request_rejects_invalid_or_coerced_dimensions(changes) -> None:
    with pytest.raises(ValidationError):
        request(**changes)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("fixture", False),
        ("provider", "wrong-provider"),
        ("instrument", "OTHER-USDT"),
        ("market", "stocks"),
        ("timeframe", "4h"),
        ("source_timestamp", AS_OF + timedelta(seconds=1)),
        ("source_timestamp", AS_OF - timedelta(hours=1)),
        ("source_timestamp", AS_OF.replace(tzinfo=None)),
    ],
)
def test_identity_and_provenance_mismatches_are_rejected(field, value) -> None:
    provider = FixtureProvider()
    setattr(provider.data, field, value)
    with pytest.raises(DataAcquisitionError, match="invalid_snapshot"):
        service(provider).fetch(request())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("open", float("nan")),
        ("close", float("inf")),
        ("close", -1),
        ("open", True),
        ("high", 1),
        ("volume", -1),
        ("volume", True),
        ("complete", False),
        ("timestamp", AS_OF + timedelta(hours=1)),
    ],
)
def test_unsafe_or_unclosed_candles_never_reach_analysis(field, value) -> None:
    provider = FixtureProvider()
    setattr(provider.data.candles[-1], field, value)
    with pytest.raises(DataAcquisitionError, match="invalid_snapshot"):
        service(provider).analyze(request())


def test_gap_duplicate_staleness_and_coverage_limits_are_rejected() -> None:
    providers = [FixtureProvider() for _ in range(5)]
    providers[0].data.candles.pop(2)
    providers[1].data.candles[2].timestamp = providers[1].data.candles[1].timestamp
    providers[2].data.candles = providers[2].data.candles[:1]
    providers[3].data.candles = providers[3].data.candles[-2:]
    # Extra observations cannot silently overflow a caller's requested bound.
    queries = [
        request(),
        request(),
        request(),
        request(minimum_candles=3),
        request(limit=4),
    ]
    for provider, query in zip(providers, queries, strict=True):
        with pytest.raises(DataAcquisitionError, match="invalid_snapshot"):
            service(provider).fetch(query)


def test_retryable_failures_have_bounded_explicit_waits() -> None:
    provider = FixtureProvider([TransientProviderError(), TransientProviderError(0.5)])
    waits = []
    data = service(provider, wait=waits.append).fetch(request())
    assert data.fixture is True
    assert provider.calls == 3
    assert waits == [0.1, 0.5]


def test_exhaustion_does_not_sleep_or_call_after_final_attempt() -> None:
    provider = FixtureProvider([TransientProviderError() for _ in range(4)])
    waits = []
    with pytest.raises(DataAcquisitionError, match="provider_unavailable"):
        service(provider, wait=waits.append).fetch(request())
    assert provider.calls == 3
    assert waits == [0.1, 0.2]


@pytest.mark.parametrize("retry_after", [True, -1, float("nan"), float("inf"), 20])
def test_unsafe_retry_after_is_not_used_or_shortened(retry_after) -> None:
    provider = FixtureProvider([TransientProviderError(retry_after)])
    waits = []
    with pytest.raises(DataAcquisitionError, match="provider_unavailable"):
        service(provider, wait=waits.append).fetch(request())
    assert provider.calls == 1
    assert waits == []


def test_permanent_errors_are_sanitized_without_retries() -> None:
    provider = FixtureProvider([RuntimeError("private-provider-token")])
    with pytest.raises(DataAcquisitionError) as raised:
        service(provider).fetch(request())
    assert str(raised.value) == "provider_unavailable"
    assert provider.calls == 1


def test_acquired_fixture_uses_existing_production_service_and_provenance() -> None:
    result = service().analyze(request())
    assert len(result.outputs) == 28
    data = next(output for output in result.outputs if output.engine_name == "data")
    assert data.data["provider"] == "contract-fixture"
    assert data.data["fixture"] is True
    assert all(
        evidence.provenance["provider"] == "contract-fixture"
        for output in result.outputs
        for evidence in output.evidence
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"max_attempts": True},
        {"max_attempts": 6},
        {"base_delay": -1},
        {"maximum_delay": float("inf")},
        {"maximum_delay": 11},
        {"base_delay": 3, "maximum_delay": 2},
    ],
)
def test_invalid_retry_policy_is_rejected(changes) -> None:
    with pytest.raises(ValueError):
        RetryPolicy(**changes)
