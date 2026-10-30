"""Bounded request/as-of snapshot cache; no cross-request mutable sharing."""

from collections import OrderedDict
from collections.abc import Callable
from math import isfinite
from threading import Lock
from time import monotonic

from app.analysis.data_contracts import MarketDataRequest
from app.analysis.models import MarketData


class SnapshotCache:
    def __init__(
        self,
        *,
        maximum_entries: int = 32,
        ttl_seconds: float = 30.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if type(maximum_entries) is not int or not 1 <= maximum_entries <= 128:
            raise ValueError("Cache entries must be an integer in [1, 128]")
        if (
            isinstance(ttl_seconds, bool)
            or not isinstance(ttl_seconds, int | float)
            or not isfinite(ttl_seconds)
            or not 0 < ttl_seconds <= 300
        ):
            raise ValueError("Cache TTL must be finite in (0, 300] seconds")
        self._maximum_entries = maximum_entries
        self._ttl = ttl_seconds
        self._clock = clock
        self._entries: OrderedDict[MarketDataRequest, tuple[float, MarketData]] = (
            OrderedDict()
        )
        self._lock = Lock()

    def get(self, request: MarketDataRequest) -> MarketData | None:
        with self._lock:
            entry = self._entries.get(request)
            if entry is None:
                return None
            expires_at, data = entry
            if self._clock() >= expires_at:
                del self._entries[request]
                return None
            self._entries.move_to_end(request)
            return data.model_copy(deep=True)

    def put(self, request: MarketDataRequest, data: MarketData) -> None:
        with self._lock:
            self._entries[request] = (
                self._clock() + self._ttl,
                data.model_copy(deep=True),
            )
            self._entries.move_to_end(request)
            while len(self._entries) > self._maximum_entries:
                self._entries.popitem(last=False)
