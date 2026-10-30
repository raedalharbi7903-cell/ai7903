import { expect, it } from "vitest";
import { parseWatchlistItem, parseWatchlistPage } from "./watchlist";
import { watchlistItem, watchlistPage } from "../test/watchlist";
import { createFixture } from "../features/analysis/fixture";
import { timeframes } from "./analysis";

it.each(timeframes)(
  "accepts supported %s and generates correctly spaced synthetic candles",
  (timeframe) => {
    expect(parseWatchlistItem({ ...watchlistItem, timeframe }).timeframe).toBe(
      timeframe,
    );
    const request = createFixture("BTC-USDT", timeframe);
    const minutes = { "1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440 }[
      timeframe
    ];
    expect(
      Date.parse(request.market_data.candles[1].timestamp) -
        Date.parse(request.market_data.candles[0].timestamp),
    ).toBe(minutes * 60000);
    expect(request.market_data.fixture).toBe(true);
    expect(request.market_data.provider).toBe("synthetic_demo");
  },
);
it.each([
  { pair: "btc-usdt" },
  { pair: "<script>" },
  { pair: "A".repeat(33) },
  { timeframe: "fixture" },
  { timeframe: "1s" },
  { id: "bad" },
  { expires_at: watchlistItem.created_at },
  { created_at: "2026-01-01" },
])("rejects invalid watchlist data %j", (change) => {
  expect(() => parseWatchlistItem({ ...watchlistItem, ...change })).toThrow();
});
it("rejects duplicate preferences, duplicate IDs, mismatched cursor and unknown version", () => {
  for (const value of [
    { ...watchlistPage(), items: [watchlistItem, watchlistItem] },
    {
      ...watchlistPage(),
      items: [
        watchlistItem,
        { ...watchlistItem, id: "00000000-0000-4000-8000-000000000002" },
      ],
    },
    {
      ...watchlistPage(),
      next_cursor: { ...watchlistItem, id: "00000000-0000-4000-8000-000000000002" },
    },
    { ...watchlistPage(), contract_version: "2.0" },
  ])
    expect(() => parseWatchlistPage(value)).toThrow();
});
