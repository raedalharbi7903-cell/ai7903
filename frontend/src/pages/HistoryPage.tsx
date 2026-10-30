import { useEffect, useRef, useState } from "react";
import { AnalysisResults } from "../features/analysis/AnalysisResults";
import { formatUtcTimestamp } from "../i18n/ar";
import {
  requestHistoryEntry,
  requestHistoryPage,
  historyMessages,
} from "../services/history";
import { ApiClientError } from "../services/http";
import type {
  HistoryCursor,
  HistoryEntry,
  HistoryPage as Page,
} from "../types/history";

export function HistoryPage() {
  const [page, setPage] = useState<Page | null>(null);
  const [selected, setSelected] = useState<HistoryEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);

  async function read(identifier?: string, cursor?: HistoryCursor) {
    if (loading) return;
    const controller = new AbortController();
    active.current?.abort();
    active.current = controller;
    setLoading(true);
    setError(null);
    setSelected(null);
    try {
      if (identifier) {
        const entry = await requestHistoryEntry(identifier, controller.signal);
        if (!controller.signal.aborted) setSelected(entry);
      } else {
        const result = await requestHistoryPage(cursor, controller.signal);
        if (!controller.signal.aborted) setPage(result);
      }
    } catch (reason) {
      if (!controller.signal.aborted) {
        setError(
          reason instanceof ApiClientError
            ? reason.message
            : historyMessages.unavailable,
        );
        setPage(null);
        setSelected(null);
      }
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }

  return (
    <div>
      <header className="hero">
        <h1>سجل التحليلات</h1>
        <p>قراءة نتائج محفوظة سابقاً؛ لا تُنفّذ هذه الصفحة تحليلاً جديداً.</p>
      </header>
      <aside className="demo-notice" aria-label="حدود سجل التحليلات">
        تتطلب القراءة جلسة موثوقة وسياسة احتفاظ مفعّلة. موفّر تسجيل الدخول غير مفعّل في
        هذه النسخة؛ لا توجد جلسة تجريبية تمنح الوصول. لا يُحفظ التحليل تلقائياً عند
        استخدام المساحة التجريبية.
      </aside>
      <div className="my-6 flex flex-wrap gap-4">
        <button disabled={loading} onClick={() => void read()}>
          تحميل السجل
        </button>
        {page?.next_cursor && !selected && (
          <button
            disabled={loading}
            onClick={() => void read(undefined, page.next_cursor ?? undefined)}
          >
            الصفحة التالية
          </button>
        )}
        {selected && (
          <button disabled={loading} onClick={() => setSelected(null)}>
            العودة إلى القائمة
          </button>
        )}
      </div>
      {loading && <p role="status">جارٍ قراءة السجل…</p>}
      {error && (
        <p role="alert" className="error-panel">
          {error}
        </p>
      )}
      {!loading && !error && !page && <p>لم يُطلب تحميل السجل بعد.</p>}
      {!loading && !error && page && !selected && (
        <section className="panel" aria-label="السجلات المحفوظة">
          {page.items.length === 0 ? (
            <p>لا توجد سجلات متاحة في هذه الصفحة.</p>
          ) : (
            <ul className="space-y-4">
              {page.items.map((item) => (
                <li key={item.id}>
                  <p>
                    حُفظ في{" "}
                    <time dateTime={item.created_at} dir="ltr">
                      {formatUtcTimestamp(item.created_at)}
                    </time>
                  </p>
                  <p>
                    انتهاء الاحتفاظ{" "}
                    <time dateTime={item.expires_at} dir="ltr">
                      {formatUtcTimestamp(item.expires_at)}
                    </time>
                  </p>
                  <button
                    onClick={() => void read(item.id)}
                    aria-label={`فتح السجل ${item.id}`}
                  >
                    عرض النتيجة المحفوظة
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
      {selected && !loading && !error && (
        <section aria-label="نتيجة محفوظة">
          <p>هذه نتيجة سابقة بوقت إنشائها الأصلي، وليست تحديثاً للسوق.</p>
          <AnalysisResults result={selected.result} />
        </section>
      )}
    </div>
  );
}
