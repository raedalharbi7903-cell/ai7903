import type { Timeframe } from "./analysis";
import { timeframes } from "./analysis";
import { parseHistoryPage } from "./history";
import type { HistoryCursor, HistoryHeader } from "./history";

export interface WatchlistSelection {
  pair: string;
  timeframe: Timeframe;
}
export interface WatchlistItem extends HistoryHeader, WatchlistSelection {}
export interface WatchlistPage {
  contract_version: "1.0";
  items: WatchlistItem[];
  next_cursor: HistoryCursor | null;
}
export function validPair(value: unknown): value is string {
  return (
    typeof value === "string" &&
    value.length <= 32 &&
    /^[A-Z0-9]+-[A-Z0-9]+$/.test(value)
  );
}
export function validTimeframe(value: unknown): value is Timeframe {
  return timeframes.some((timeframe) => timeframe === value);
}
export function parseWatchlistPage(value: unknown): WatchlistPage {
  // Share the existing UUID/time/expiry/cursor/duplicate-ID metadata boundary.
  const metadata = parseHistoryPage(value);
  if (
    !value ||
    typeof value !== "object" ||
    !("items" in value) ||
    !Array.isArray(value.items)
  ) {
    throw new Error("Invalid watchlist page");
  }
  const rows = value.items;
  const items = metadata.items.map((header, index): WatchlistItem => {
    const row: unknown = rows[index];
    if (
      !row ||
      typeof row !== "object" ||
      !("pair" in row) ||
      !validPair(row.pair) ||
      !("timeframe" in row) ||
      !validTimeframe(row.timeframe)
    ) {
      throw new Error("Invalid watchlist selection");
    }
    return { ...header, pair: row.pair, timeframe: row.timeframe };
  });
  if (
    new Set(items.map((item) => `${item.pair}/${item.timeframe}`)).size !== items.length
  ) {
    throw new Error("Duplicate watchlist selection");
  }
  return { ...metadata, items };
}
export function parseWatchlistItem(value: unknown): WatchlistItem {
  return parseWatchlistPage({
    contract_version: "1.0",
    items: [value],
    next_cursor: null,
  }).items[0];
}
