import { requestJson } from "./http";
import { parseSubscription, parseBillingHistory } from "../types/billing";
import type { HistoryCursor } from "../types/history";

export const billingMessages = {
  unavailable: "تعذّر تنفيذ طلب الاشتراك. حاول مجدداً.",
  invalidResponse: "تعذّر التحقق من استجابة الاشتراك.",
  statuses: {
    401: "يلزم تسجيل دخول موثوق لعرض الاشتراك.",
    403: "لا تملك صلاحية تنفيذ هذا الطلب.",
    404: "لا يوجد سجل متاح لهذا الإجراء.",
    409: "تغيّرت حالة الاشتراك؛ حدّث الحالة قبل المحاولة مجدداً.",
    503: "خدمة الاشتراك والدفع غير مفعّلة حالياً.",
  },
};
export function requestSubscription(signal?: AbortSignal) {
  return requestJson(
    "/billing/subscription",
    { method: "GET", signal },
    parseSubscription,
    billingMessages,
  );
}
export function requestBillingHistory(cursor?: HistoryCursor, signal?: AbortSignal) {
  const query = new URLSearchParams({ limit: "20" });
  if (cursor) {
    query.set("before_id", cursor.id);
    query.set("before_created_at", cursor.created_at);
  }
  return requestJson(
    `/billing/history?${query}`,
    { method: "GET", signal },
    parseBillingHistory,
    billingMessages,
  );
}
export function requestCancellation(signal?: AbortSignal) {
  return requestJson(
    "/billing/subscription/cancel",
    {
      method: "POST",
      body: "{}",
      headers: { "Content-Type": "application/json" },
      signal,
    },
    (value) => {
      const result = parseSubscription(value);
      if (!result.cancel_at_period_end) throw new Error("Cancellation not recorded");
      return result;
    },
    billingMessages,
  );
}
