"""Requirement: DATA-CACHE. No real data, provider or elapsed-time sleeps."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest

from app.analysis.data_cache import SnapshotCache
from app.analysis.data_contracts import DataAcquisitionError
from tests.analysis.test_data_acquisition import FixtureProvider, request, service


def test_cache_deep_copies_both_ingress_and_egress_and_expires() -> None:
    now = [0.0]
    cache = SnapshotCache(ttl_seconds=2, clock=lambda: now[0])
    data = FixtureProvider().data
    cache.put(request(), data)
    data.candles[0].close = 500
    first = cache.get(request())
    assert first is not None
    assert first.candles[0].close == 10
    first.candles[0].close = 600
    assert cache.get(request()).candles[0].close == 10
    now[0] = 2
    assert cache.get(request()) is None


def test_cache_keys_include_asof_instrument_timeframe_limit_and_coverage() -> None:
    cache = SnapshotCache()
    cache.put(request(), FixtureProvider().data)
    for changes in [
        {"as_of": request().as_of - timedelta(hours=1)},
        {"instrument": "OTHER-USDT"},
        {"timeframe": "4h"},
        {"limit": 4},
        {"minimum_candles": 2},
    ]:
        assert cache.get(request(**changes)) is None


def test_cache_lru_is_bounded_and_reads_refresh_lru_position() -> None:
    cache = SnapshotCache(maximum_entries=2)
    data = FixtureProvider().data
    first, second, third = [request(instrument=f"TEST{i}-USDT") for i in range(3)]
    cache.put(first, data)
    cache.put(second, data)
    assert cache.get(first) is not None
    cache.put(third, data)
    assert cache.get(second) is None
    assert cache.get(first) is not None
    assert cache.get(third) is not None


def test_cache_concurrent_readers_cannot_mutate_shared_results() -> None:
    cache = SnapshotCache()
    cache.put(request(), FixtureProvider().data)

    def mutate(index):
        data = cache.get(request())
        assert data.candles[0].close == 10
        data.candles[0].close = index + 100

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(mutate, range(64)))
    assert cache.get(request()).candles[0].close == 10


def test_service_reuses_only_its_own_validated_fixture_snapshot() -> None:
    provider = FixtureProvider()
    acquisition = service(provider, cache_ttl_seconds=30)
    first = acquisition.fetch(request())
    first.candles[0].close = 900
    assert acquisition.fetch(request()).candles[0].close == 10
    assert provider.calls == 1
    assert service(provider, cache_ttl_seconds=30).fetch(request()).fixture is True
    assert provider.calls == 2


@pytest.mark.parametrize(
    ("field", "value"),
    [("mode", "live"), ("provider_id", "changed-identity")],
)
def test_cache_cannot_bypass_mode_or_provider_identity_guards(field, value) -> None:
    provider = FixtureProvider()
    acquisition = service(provider, cache_ttl_seconds=30)
    acquisition.fetch(request())
    setattr(provider, field, value)
    with pytest.raises(DataAcquisitionError):
        acquisition.fetch(request())
    assert provider.calls == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_entries": True},
        {"maximum_entries": 0},
        {"maximum_entries": 129},
        {"ttl_seconds": True},
        {"ttl_seconds": 0},
        {"ttl_seconds": float("nan")},
        {"ttl_seconds": float("inf")},
        {"ttl_seconds": 301},
    ],
)
def test_cache_rejects_invalid_resource_bounds(changes) -> None:
    with pytest.raises(ValueError):
        SnapshotCache(**changes)
