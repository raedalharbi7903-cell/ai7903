import { historyHeader } from "./history";
export const watchlistItem = {
  ...historyHeader,
  pair: "BTC-USDT",
  timeframe: "1h" as const,
};
export function watchlistPage() {
  return {
    contract_version: "1.0" as const,
    items: [{ ...watchlistItem }],
    next_cursor: null,
  };
}
