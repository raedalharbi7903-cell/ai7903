from math import isfinite

from app.analysis.data_contracts import DataAcquisitionError
from app.analysis.models import MarketData, ValidationStatus


class OkxProvider:
    """Legacy compatibility boundary; unapproved live access is always denied.

    Future licensed adapters must use the reviewed provider-neutral acquisition
    contract. Merely setting a URL/API key cannot grant commercial permission.
    """

    def candles(self, symbol: str, timeframe: str, outputsize: int = 200) -> MarketData:
        raise DataAcquisitionError("live_access_unapproved")


def validate_market_data(data: MarketData) -> ValidationStatus:
    stamps = [c.timestamp for c in data.candles]
    if any(stamp.tzinfo is None for stamp in stamps):
        return ValidationStatus.FAIL
    if len(stamps) != len(set(stamps)):
        return ValidationStatus.FAIL
    if any(
        any(
            not isfinite(value) or value <= 0
            for value in (c.open, c.high, c.low, c.close)
        )
        or (c.volume is not None and (not isfinite(c.volume) or c.volume < 0))
        or c.low > min(c.open, c.close)
        or c.high < max(c.open, c.close)
        for c in data.candles
    ):
        return ValidationStatus.FAIL
    if any(
        later <= earlier for earlier, later in zip(stamps, stamps[1:], strict=False)
    ):
        return ValidationStatus.FAIL
    return ValidationStatus.PASS
