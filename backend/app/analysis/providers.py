from datetime import UTC, datetime
from typing import Protocol

import httpx

from app.analysis.models import Candle, MarketData, ValidationStatus


class MarketDataProvider(Protocol):
    def candles(
        self, symbol: str, market: str, timeframe: str, outputsize: int
    ) -> MarketData: ...


class TwelveDataProvider:
    """Adapter for Twelve Data; commercial display rights remain license-required."""

    def __init__(
        self, api_key: str, base_url: str, timeout_seconds: float = 10.0
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def candles(
        self, symbol: str, market: str, timeframe: str, outputsize: int = 200
    ) -> MarketData:
        if market not in {"us_equity", "crypto"}:
            raise ValueError("Only us_equity and crypto are supported by this MVP")
        response = httpx.get(
            f"{self._base_url}/time_series",
            params={
                "symbol": symbol,
                "interval": timeframe,
                "outputsize": outputsize,
                "apikey": self._api_key,
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if "values" not in payload:
            raise ValueError(payload.get("message", "Provider returned no candles"))
        values = list(reversed(payload["values"]))
        candles = [
            Candle(
                timestamp=item["datetime"],
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
                volume=float(item["volume"]) if item.get("volume") else None,
            )
            for item in values
        ]
        return MarketData(
            instrument=symbol,
            market=market,
            timeframe=timeframe,
            provider="twelve_data",
            exchange=payload.get("meta", {}).get("exchange"),
            asset_type="equity" if market == "us_equity" else "crypto",
            source_timestamp=candles[-1].timestamp,
            candles=candles,
            fixture=False,
            quality_status=ValidationStatus.PASS,
        )


def validate_market_data(data: MarketData) -> ValidationStatus:
    timestamps = [candle.timestamp for candle in data.candles]
    if len(timestamps) != len(set(timestamps)):
        return ValidationStatus.FAIL
    if any(
        candle.low > min(candle.open, candle.close)
        or candle.high < max(candle.open, candle.close)
        for candle in data.candles
    ):
        return ValidationStatus.FAIL
    if any(candle.low < 0 or candle.high <= 0 for candle in data.candles):
        return ValidationStatus.FAIL
    if data.source_timestamp > datetime.now(UTC):
        return ValidationStatus.DEGRADED
    return ValidationStatus.PASS
