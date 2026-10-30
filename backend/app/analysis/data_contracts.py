"""Provider-neutral acquisition contracts. Requirements: DATA-CONTRACT/DATA-RETRY."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal, Protocol

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.analysis.models import MarketData


class MarketDataRequest(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    instrument: str = Field(pattern=r"^[A-Z0-9]+-[A-Z0-9]+$", max_length=32)
    timeframe: Literal["1h", "4h", "1d"]
    as_of: AwareDatetime
    limit: int = Field(default=200, ge=1, le=5000)
    minimum_candles: int = Field(default=1, ge=1, le=5000)

    @model_validator(mode="after")
    def bounded_coverage(self) -> "MarketDataRequest":
        if self.minimum_candles > self.limit:
            raise ValueError("Minimum coverage cannot exceed requested limit")
        return self


class MarketDataProvider(Protocol):
    """Trusted adapter; must bound its own I/O timeout and never invent candles."""

    provider_id: str
    mode: Literal["fixture", "live"]

    def fetch(self, request: MarketDataRequest) -> MarketData: ...


class DataAcquisitionError(Exception):
    """Only a bounded category is safe for a consumer; never expose raw errors."""

    def __init__(
        self,
        category: Literal[
            "provider_unavailable", "live_access_unapproved", "invalid_snapshot"
        ],
    ) -> None:
        self.category = category
        super().__init__(category)


class TransientProviderError(Exception):
    """Adapter-classified timeout/rate limit; optional Retry-After is in seconds."""

    def __init__(self, retry_after: float | None = None) -> None:
        self.retry_after = retry_after
        super().__init__("transient_provider_error")


@dataclass(frozen=True)
class RetryPolicy:
    """Operational retry bounds, not analytical calibration parameters."""

    max_attempts: int = 3
    base_delay: float = 0.1
    maximum_delay: float = 2.0

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 5:
            raise ValueError("Retry attempts must be an integer in [1, 5]")
        if any(
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not isfinite(value)
            or value < 0
            for value in (self.base_delay, self.maximum_delay)
        ):
            raise ValueError("Retry delays must be finite nonnegative numbers")
        if not self.base_delay <= self.maximum_delay <= 10:
            raise ValueError("Retry delays must be ordered and at most ten seconds")

    def delay(self, failed_attempt: int, retry_after: float | None) -> float:
        if retry_after is not None:
            if (
                isinstance(retry_after, bool)
                or not isinstance(retry_after, int | float)
                or not isfinite(retry_after)
                or not 0 <= retry_after <= self.maximum_delay
            ):
                # Do not retry sooner than a provider's required wait.
                raise DataAcquisitionError("provider_unavailable")
            return float(retry_after)
        return min(self.base_delay * 2 ** (failed_attempt - 1), self.maximum_delay)
