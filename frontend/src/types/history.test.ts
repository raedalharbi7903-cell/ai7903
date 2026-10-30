import { describe, expect, it } from "vitest";
import { parseHistoryEntry, parseHistoryPage } from "./history";
import { historyEntry, historyHeader, historyPage } from "../test/history";
import { parseWatchlistItem } from "./watchlist";

describe("private history contracts", () => {
  it("parses metadata pages and full saved results separately", () => {
    expect(parseHistoryPage(historyPage())).toEqual(historyPage());
    expect(parseHistoryEntry(historyEntry()).result.decision).toBe("wait");
    expect(parseHistoryPage(historyPage()).items[0]).not.toHaveProperty("result");
  });
  it.each([
    null,
    {},
    { ...historyPage(), contract_version: "2.0" },
    { ...historyPage(), items: [historyHeader, historyHeader] },
    { ...historyPage(), items: Array(101).fill(historyHeader) },
    { ...historyPage(), items: [{ ...historyHeader, id: "../other-owner" }] },
    {
      ...historyPage(),
      items: [{ ...historyHeader, created_at: "2026-01-01T00:00:00" }],
    },
    {
      ...historyPage(),
      items: [{ ...historyHeader, expires_at: historyHeader.created_at }],
    },
    {
      ...historyPage(),
      next_cursor: { id: "wrong", created_at: historyHeader.created_at },
    },
    {
      ...historyPage(),
      next_cursor: { id: historyHeader.id, created_at: "2025-01-01T00:00:00Z" },
    },
  ])(
    "rejects incompatible, duplicate, naive, unsafe or mismatched page %j",
    (value) => {
      expect(() => parseHistoryPage(value)).toThrow();
    },
  );
  it("rejects a saved entry with incompatible analysis rather than fabricating a result", () => {
    expect(() => parseHistoryEntry({ ...historyEntry(), result: {} })).toThrow();
  });
  it.each([
    "2026-02-29T00:00:00Z",
    "2026-02-30T00:00:00+00:00",
    "2024-04-31T00:00:00-03:00",
    "1900-02-29T00:00:00Z",
    "2100-02-29T00:00:00Z",
    "0000-01-01T00:00:00Z",
    "2026-01-01T24:00:00Z",
    "2026-01-01T23:60:00Z",
    "2026-01-01T23:59:60Z",
    "2026-01-01T23:59:59+24:00",
    "2026-01-01T23:59:59+01:60",
  ])("rejects impossible calendar/time/offset value %s", (created_at) => {
    const item = {
      ...historyHeader,
      created_at,
      expires_at: "9999-12-31T23:59:59.999999Z",
    };
    expect(() =>
      parseHistoryPage({
        contract_version: "1.0",
        items: [item],
        next_cursor: null,
      }),
    ).toThrow();
    expect(() =>
      parseWatchlistItem({
        ...item,
        pair: "BTC-USDT",
        timeframe: "1h",
      }),
    ).toThrow();
  });
  it.each([
    "0001-01-01T00:00:00Z",
    "0099-02-28T00:00:00+00:00",
    "2000-02-29T23:59:59.123456+03:00",
    "2024-02-29T00:00:00-23:59",
    "2026-10-31T12:30:45.123456789Z",
    "9999-12-30T23:59:59+23:59",
  ])("preserves valid aware ISO value without normalization %s", (created_at) => {
    const item = {
      ...historyHeader,
      created_at,
      expires_at: "9999-12-31T23:59:59.999999Z",
    };
    expect(
      parseHistoryPage({
        contract_version: "1.0",
        items: [item],
        next_cursor: null,
      }).items[0].created_at,
    ).toBe(created_at);
    expect(
      parseWatchlistItem({
        ...item,
        pair: "BTC-USDT",
        timeframe: "1h",
      }).created_at,
    ).toBe(created_at);
  });
});
