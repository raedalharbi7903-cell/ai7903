import { requestJson, ApiClientError } from "./http";
import { parseHistoryEntry, parseHistoryPage, validHistoryId } from "../types/history";
import type { HistoryCursor } from "../types/history";

export const historyMessages = {
  unavailable: "تعذّر قراءة السجل. حاول مجدداً.",
  invalidResponse: "تعذّر التحقق من استجابة سجل التحليلات.",
  statuses: {
    401: "يلزم تسجيل دخول موثوق لعرض سجل التحليلات.",
    403: "لا تملك صلاحية الوصول إلى هذا السجل.",
    404: "السجل غير متاح أو انتهت صلاحيته.",
    503: "سجل التحليلات غير مفعّل حالياً.",
  },
};

export function requestHistoryPage(cursor?: HistoryCursor, signal?: AbortSignal) {
  const query = new URLSearchParams({ limit: "20" });
  if (cursor) {
    query.set("before_created_at", cursor.created_at);
    query.set("before_id", cursor.id);
  }
  return requestJson(
    `/history?${query.toString()}`,
    { method: "GET", signal },
    parseHistoryPage,
    historyMessages,
  );
}
export function requestHistoryEntry(identifier: string, signal?: AbortSignal) {
  if (!validHistoryId(identifier)) {
    return Promise.reject(new ApiClientError(historyMessages.invalidResponse));
  }
  return requestJson(
    `/history/${identifier}`,
    { method: "GET", signal },
    (value) => {
      const entry = parseHistoryEntry(value);
      if (entry.id.toLowerCase() !== identifier.toLowerCase()) {
        throw new Error("History response identifier mismatch");
      }
      return entry;
    },
    historyMessages,
  );
}
