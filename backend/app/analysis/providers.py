from datetime import UTC, datetime

import httpx

from app.analysis.models import Candle, MarketData, ValidationStatus


class OkxProvider:
    """Development/test only; commercial OKX data rights require written approval."""

    def candles(self, symbol: str, timeframe: str, outputsize: int = 200) -> MarketData:
        response = httpx.get(
            "https://www.okx.com/api/v5/market/history-candles",
            params={"instId": symbol, "bar": timeframe, "limit": outputsize},
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != "0" or not payload.get("data"):
            raise ValueError(payload.get("msg", "OKX returned no candles"))
        candles = [
            Candle(
                timestamp=datetime.fromtimestamp(int(row[0]) / 1000, UTC),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in reversed(payload["data"])
        ]
        data = MarketData(
            instrument=symbol,
            market="crypto",
            timeframe=timeframe,
            provider="okx",
            exchange="OKX",
            asset_type="crypto",
            source_timestamp=candles[-1].timestamp,
            candles=candles,
        )
        data.quality_status = validate_market_data(data)
        return data


def validate_market_data(data: MarketData) -> ValidationStatus:
    stamps = [c.timestamp for c in data.candles]
    if len(stamps) != len(set(stamps)):
        return ValidationStatus.FAIL
    if any(
        c.low < 0
        or c.high <= 0
        or c.low > min(c.open, c.close)
        or c.high < max(c.open, c.close)
        for c in data.candles
    ):
        return ValidationStatus.FAIL
    return (
        ValidationStatus.DEGRADED
        if data.source_timestamp > datetime.now(UTC)
        else ValidationStatus.PASS
    )
