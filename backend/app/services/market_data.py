"""Validated acquisition into the existing AnalysisService, not a second pipeline."""

from collections.abc import Callable
from datetime import UTC
from time import sleep

from app.analysis.data_cache import SnapshotCache
from app.analysis.data_contracts import (
    DataAcquisitionError,
    MarketDataProvider,
    MarketDataRequest,
    RetryPolicy,
    TransientProviderError,
)
from app.analysis.freshness import FreshnessPolicy, assess_market_data
from app.analysis.models import (
    AnalysisInput,
    AnalysisResult,
    FreshnessStatus,
    MarketData,
    ValidationStatus,
)
from app.analysis.providers import validate_market_data
from app.analysis.service import AnalysisService


class MarketDataService:
    """Fixture contract environment only until real provider rights are approved.

    No adapter is selected by default. Even an injected live adapter is rejected
    before fetch; a constructor flag is not treated as commercial license evidence.
    All current public API behavior, including production denial, is unchanged.
    """

    def __init__(
        self,
        provider: MarketDataProvider | None = None,
        *,
        fixture_enabled: bool = False,
        retry_policy: RetryPolicy | None = None,
        wait: Callable[[float], None] = sleep,
        analysis: AnalysisService | None = None,
        cache_ttl_seconds: float | None = None,
    ) -> None:
        self._provider = provider
        self._provider_id = provider.provider_id if provider is not None else None
        self._fixture_enabled = fixture_enabled
        self._retry = retry_policy or RetryPolicy()
        self._wait = wait
        self._analysis = analysis or AnalysisService()
        # Cache is private to this provider/service instance, never shared by ID.
        self._cache = (
            SnapshotCache(ttl_seconds=cache_ttl_seconds)
            if cache_ttl_seconds is not None
            else None
        )

    def fetch(self, request: MarketDataRequest) -> MarketData:
        provider = self._provider
        if provider is None:
            raise DataAcquisitionError("provider_unavailable")
        if provider.mode != "fixture":
            raise DataAcquisitionError("live_access_unapproved")
        if (
            self._fixture_enabled is not True
            or not isinstance(provider.provider_id, str)
            or not provider.provider_id.strip()
            or provider.provider_id != self._provider_id
        ):
            raise DataAcquisitionError("provider_unavailable")
        if self._cache is not None:
            cached = self._cache.get(request)
            if cached is not None:
                return cached
        for attempt in range(1, self._retry.max_attempts + 1):
            try:
                raw = provider.fetch(request)
            except TransientProviderError as error:
                if attempt == self._retry.max_attempts:
                    raise DataAcquisitionError("provider_unavailable") from None
                self._wait(self._retry.delay(attempt, error.retry_after))
                continue
            except Exception:
                raise DataAcquisitionError("provider_unavailable") from None
            data = self._validate(raw, request, provider.provider_id)
            if self._cache is not None:
                self._cache.put(request, data)
            return data
        raise DataAcquisitionError("provider_unavailable")

    @staticmethod
    def _validate(
        raw: MarketData, request: MarketDataRequest, provider_id: str
    ) -> MarketData:
        try:
            if raw.fixture is not True or any(
                type(candle.complete) is not bool
                or (
                    candle.volume is not None
                    and (
                        isinstance(candle.volume, bool)
                        or not isinstance(candle.volume, int | float)
                    )
                )
                or any(
                    isinstance(value, bool) or not isinstance(value, int | float)
                    for value in (
                        candle.open,
                        candle.high,
                        candle.low,
                        candle.close,
                    )
                )
                for candle in raw.candles
            ):
                raise ValueError("Invalid typed snapshot")
            # Revalidate even typed adapter objects; copying alone trusts mutation.
            data = MarketData.model_validate(raw.model_dump()).model_copy(deep=True)
            if (
                data.provider != provider_id
                or not data.fixture
                or data.market != "crypto"
                or data.instrument != request.instrument
                or data.timeframe != request.timeframe
                or not request.minimum_candles <= len(data.candles) <= request.limit
                or data.source_timestamp.tzinfo is None
                or data.source_timestamp > request.as_of
                or data.source_timestamp < data.candles[-1].timestamp
                or any(
                    not candle.complete or candle.timestamp > request.as_of
                    for candle in data.candles
                )
                or validate_market_data(data) != ValidationStatus.PASS
            ):
                raise ValueError("Invalid provider snapshot")
            data.source_timestamp = data.source_timestamp.astimezone(UTC)
            for candle in data.candles:
                candle.timestamp = candle.timestamp.astimezone(UTC)
            policy = FreshnessPolicy()
            interval = policy.interval_for(data.timeframe)
            if interval is None or any(
                later.timestamp - earlier.timestamp != interval
                for earlier, later in zip(data.candles, data.candles[1:], strict=False)
            ):
                raise ValueError("Incomplete coverage")
            freshness = assess_market_data(data, request.as_of, policy)
            if freshness.status not in {FreshnessStatus.FRESH, FreshnessStatus.DELAYED}:
                raise ValueError("Unavailable history")
            data.quality_status = ValidationStatus.PASS
            data.freshness_status = freshness.status
            data.freshness_reason = freshness.reason
            return data
        except (AttributeError, TypeError, ValueError):
            raise DataAcquisitionError("invalid_snapshot") from None

    def analyze(self, request: MarketDataRequest) -> AnalysisResult:
        data = self.fetch(request)
        return self._analysis.analyze(
            AnalysisInput(
                data=data.model_dump(mode="json"),
                metadata={"decision_timestamp": request.as_of.isoformat()},
            )
        )
