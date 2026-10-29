import type { AnalysisRequest, Timeframe } from "../../types/analysis";
const intervals: Record<Timeframe, number> = {
  "1h": 3600000,
  "4h": 14400000,
  "1d": 86400000,
};
/** Synthetic demonstration only. Pair labels are never actual market prices. */
export function createFixture(pair: string, timeframe: Timeframe): AnalysisRequest {
  const values = [14, 15, 10, 13, 12, 9, 12, 13, 14];
  const candles = values.map((close, index) => ({
    timestamp: new Date(
      Date.UTC(2026, 0, 1) + index * intervals[timeframe],
    ).toISOString(),
    open: close,
    high: close + 1,
    low: close - 1,
    close,
    volume: 100,
    complete: true,
  }));
  return {
    pair,
    timeframe,
    request_id: crypto.randomUUID(),
    market_data: {
      instrument: pair,
      market: "crypto",
      timeframe,
      provider: "synthetic_demo",
      source_timestamp: candles[candles.length - 1].timestamp,
      fixture: true,
      candles,
    },
    metadata: { timeframes: {} },
  };
}
