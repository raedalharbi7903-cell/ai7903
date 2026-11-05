import { useEffect, useRef, useState } from "react";
import { ApiClientError } from "../services/http";
import {
  billingMessages,
  requestSubscription,
  requestCancellation,
  requestBillingHistory,
} from "../services/billing";
import type { SubscriptionSummary, BillingHistoryPage } from "../types/billing";
import type { HistoryCursor } from "../types/history";
import { formatUtcTimestamp } from "../i18n/ar";

const states: Record<SubscriptionSummary["state"], string> = {
  none: "لا توجد فترة مدفوعة مسجلة",
  active: "فترة مدفوعة سارية في السجل",
  scheduled: "فترة مدفوعة لم تبدأ بعد",
  expired: "انتهت الفترة المدفوعة المسجلة",
  review_required: "الحالة تتطلب مراجعة",
};
const kinds: Record<string, string> = {
  paid: "حدث دفع موثّق في السجل",
  payment_failed: "إخفاق دفع مبلّغ عنه",
  refund: "حدث استرداد يحتاج مراجعة",
  dispute: "حدث اعتراض يحتاج مراجعة",
  unsupported: "حدث غير مدعوم يحتاج مراجعة",
};

export function SubscriptionPage() {
  const [summary, setSummary] = useState<SubscriptionSummary | null>(null);
  const [history, setHistory] = useState<BillingHistoryPage | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirm, setConfirm] = useState(false);
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);
  function clearPrivate() {
    setSummary(null);
    setHistory(null);
    setConfirm(false);
  }
  async function perform(action: (signal: AbortSignal) => Promise<void>) {
    if (busy) return;
    const controller = new AbortController();
    active.current?.abort();
    active.current = controller;
    setBusy(true);
    setError(null);
    setNotice(null);
    setConfirm(false);
    try {
      await action(controller.signal);
    } catch (reason) {
      if (!controller.signal.aborted) {
        clearPrivate();
        setError(
          reason instanceof ApiClientError
            ? reason.message
            : billingMessages.unavailable,
        );
      }
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }
  function loadSummary() {
    return perform(async (signal) => {
      const value = await requestSubscription(signal);
      if (!signal.aborted) setSummary(value);
    });
  }
  function loadHistory(cursor?: HistoryCursor) {
    return perform(async (signal) => {
      const value = await requestBillingHistory(cursor, signal);
      if (!signal.aborted) setHistory(value);
    });
  }
  function cancel() {
    return perform(async (signal) => {
      const value = await requestCancellation(signal);
      if (!signal.aborted) {
        setSummary(value);
        setNotice(
          "سُجّل طلب إيقاف التجديد محلياً. لا يعني ذلك إرسال إجراء إلى مزوّد دفع.",
        );
      }
    });
  }
  return (
    <div>
      <header className="hero">
        <h1>الاشتراك وسجل الفوترة</h1>
        <p>عرض بيانات حسابك المسجلة بطلب منك.</p>
      </header>
      <aside className="demo-notice" aria-label="حدود خدمة الاشتراك">
        مزوّد الدفع غير معتمد وغير مفعّل في هذه النسخة، والسعر النهائي لم يُعتمد. لا
        توجد تجربة مجانية أو خطة سنوية أو عملية تحصيل دفع عبر هذه الصفحة. تتطلب البيانات
        جلسة موثوقة وسياسات مفعّلة؛ بيانات اختبارات التكامل مصطنعة.
      </aside>
      <div className="my-6 flex flex-wrap gap-4">
        <button disabled={busy} onClick={() => void loadSummary()}>
          تحميل حالة الاشتراك
        </button>
        <button disabled={busy} onClick={() => void loadHistory()}>
          تحميل سجل الفوترة
        </button>
      </div>
      {busy && <p role="status">جارٍ تنفيذ طلب الاشتراك…</p>}
      {error && (
        <p role="alert" className="error-panel">
          {error}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
      {!summary && !history && !error && !busy && (
        <p>لم تُحمّل بيانات اشتراك أو فوترة بعد.</p>
      )}
      {summary && !busy && (
        <section className="panel" aria-label="حالة الاشتراك">
          <h2>{states[summary.state]}</h2>
          <p>الخطة: شهرية واحدة؛ لا يُعرض سعر غير معتمد.</p>
          <p>
            {summary.entitled
              ? "يسمح السجل بوصول التحليل ضمن الفترة المسجلة."
              : "لا توجد صلاحية تحليل مدفوعة مثبتة حالياً."}
          </p>
          {summary.paid_period_start && summary.paid_period_end && (
            <p>
              الفترة المسجلة{" "}
              <time dateTime={summary.paid_period_start} dir="ltr">
                {formatUtcTimestamp(summary.paid_period_start)}
              </time>
              {" — "}
              <time dateTime={summary.paid_period_end} dir="ltr">
                {formatUtcTimestamp(summary.paid_period_end)}
              </time>
            </p>
          )}
          <p>
            {summary.cancel_at_period_end
              ? "إيقاف التجديد مسجل؛ لا يُختصر انتهاء الفترة المدفوعة."
              : summary.renewal_consent
                ? "السجل يتضمن موافقة تجديد؛ لا تُنفّذ هذه النسخة تجديداً أو تحصيلاً."
                : "لا توجد موافقة تجديد مسجلة."}
          </p>
          {summary.paid_period_end &&
            !summary.cancel_at_period_end &&
            !summary.review_required && (
              <button onClick={() => setConfirm(true)}>طلب إيقاف التجديد</button>
            )}
        </section>
      )}
      {confirm && !busy && (
        <section className="panel" aria-label="تأكيد طلب إيقاف التجديد">
          <h2>تأكيد تسجيل طلب إيقاف التجديد</h2>
          <p>
            يبقى الوصول المسجل حتى نهاية الفترة المدفوعة. لا يوجد اتصال بمزوّد دفع في
            هذه النسخة.
          </p>
          <button onClick={() => void cancel()}>تأكيد إيقاف التجديد</button>
          <button onClick={() => setConfirm(false)}>رجوع</button>
        </section>
      )}
      {history && !busy && (
        <section className="panel" aria-label="أحداث الفوترة">
          <h2>سجل أحداث الفوترة</h2>
          <p>
            ليس فاتورة ضريبية. المبالغ بوحداتها الصغرى كما في السجل، وليست سعراً معروضاً
            للاشتراك.
          </p>
          {history.items.length === 0 ? (
            <p>لا توجد أحداث متاحة في هذه الصفحة.</p>
          ) : (
            <ul className="space-y-4">
              {history.items.map((item) => (
                <li key={item.id}>
                  <h3>{kinds[item.kind]}</h3>
                  <p>
                    {item.processing_status === "review_required"
                      ? "قيد المراجعة؛ لا يُستنتج منه استحقاق جديد."
                      : "معالجة مسجلة"}
                  </p>
                  {item.amount_minor !== null && (
                    <p>
                      المبلغ بالوحدة الصغرى:{" "}
                      <span dir="ltr">
                        {item.amount_minor} {item.currency ?? ""}
                      </span>
                    </p>
                  )}
                  <time dateTime={item.recorded_at} dir="ltr">
                    {formatUtcTimestamp(item.recorded_at)}
                  </time>
                </li>
              ))}
            </ul>
          )}
          {history.next_cursor && (
            <button
              disabled={busy}
              onClick={() => void loadHistory(history.next_cursor ?? undefined)}
            >
              صفحة الفوترة التالية
            </button>
          )}
        </section>
      )}
    </div>
  );
}
