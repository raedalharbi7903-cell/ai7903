import { requestJson, requestNoContent, ApiClientError } from "./http";
import { validHistoryId } from "../types/history";
import type { HistoryCursor } from "../types/history";
import {
  parseWatchlistItem,
  parseWatchlistPage,
  validPair,
  validTimeframe,
} from "../types/watchlist";
import type { WatchlistSelection } from "../types/watchlist";

export const watchlistMessages = {
  unavailable: "تعذّر تنفيذ طلب قائمة المتابعة. حاول مجدداً.",
  invalidResponse: "تعذّر التحقق من استجابة قائمة المتابعة.",
  statuses: {
    401: "يلزم تسجيل دخول موثوق لاستخدام قائمة المتابعة.",
    403: "لا تملك صلاحية تنفيذ هذا الطلب.",
    404: "العنصر غير متاح أو انتهت صلاحيته.",
    503: "قائمة المتابعة غير مفعّلة حالياً.",
  },
};
export function requestWatchlist(cursor?: HistoryCursor, signal?: AbortSignal) {
  const query = new URLSearchParams({ limit: "20" });
  if (cursor) {
    query.set("before_created_at", cursor.created_at);
    query.set("before_id", cursor.id);
  }
  return requestJson(
    `/watchlist?${query.toString()}`,
    { method: "GET", signal },
    parseWatchlistPage,
    watchlistMessages,
  );
}
export function saveWatchlistItem(selection: WatchlistSelection, signal?: AbortSignal) {
  if (!validPair(selection.pair) || !validTimeframe(selection.timeframe)) {
    return Promise.reject(new ApiClientError("تحقق من الزوج والإطار الزمني."));
  }
  return requestJson(
    "/watchlist",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selection),
      signal,
    },
    (value) => {
      const item = parseWatchlistItem(value);
      if (item.pair !== selection.pair || item.timeframe !== selection.timeframe) {
        throw new Error("Watchlist response mismatch");
      }
      return item;
    },
    watchlistMessages,
  );
}
export function deleteWatchlistItem(identifier: string, signal?: AbortSignal) {
  if (!validHistoryId(identifier))
    return Promise.reject(new ApiClientError(watchlistMessages.invalidResponse));
  return requestNoContent(
    `/watchlist/${identifier}`,
    { method: "DELETE", signal },
    watchlistMessages,
  );
}
