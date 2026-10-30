import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router";
import { ApiClientError } from "../services/http";
import {
  deleteWatchlistItem,
  requestWatchlist,
  saveWatchlistItem,
  watchlistMessages,
} from "../services/watchlist";
import type { WatchlistItem, WatchlistPage as Page } from "../types/watchlist";
import type { Timeframe } from "../types/analysis";
import type { HistoryCursor } from "../types/history";
import { formatUtcTimestamp } from "../i18n/ar";

export function WatchlistPage() {
  const [pair, setPair] = useState("");
  const [timeframe, setTimeframe] = useState<Timeframe>("1h");
  const [page, setPage] = useState<Page | null>(null);
  const [pendingDelete, setPendingDelete] = useState<WatchlistItem | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);

  async function perform(operation: (signal: AbortSignal) => Promise<void>) {
    if (busy) return;
    const controller = new AbortController();
    active.current?.abort();
    active.current = controller;
    setBusy(true);
    setNotice(null);
    setError(null);
    try {
      await operation(controller.signal);
    } catch (reason) {
      if (!controller.signal.aborted) {
        setError(
          reason instanceof ApiClientError
            ? reason.message
            : watchlistMessages.unavailable,
        );
        setPage(null);
        setPendingDelete(null);
      }
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }
  function load(cursor?: HistoryCursor) {
    return perform(async (signal) => {
      const response = await requestWatchlist(cursor, signal);
      if (!signal.aborted) {
        setPage(response);
        setPendingDelete(null);
      }
    });
  }
  function save(event: FormEvent) {
    event.preventDefault();
    void perform(async (signal) => {
      const item = await saveWatchlistItem({ pair, timeframe }, signal);
      if (!signal.aborted) {
        setPage(null);
        setPendingDelete(null);
        setNotice(`الزوج ${item.pair} محفوظ في قائمة المتابعة. حمّل القائمة لعرضها.`);
      }
    });
  }
  function remove(item: WatchlistItem) {
    return perform(async (signal) => {
      await deleteWatchlistItem(item.id, signal);
      if (!signal.aborted) {
        setPage(null);
        setPendingDelete(null);
        setNotice("أُزيل العنصر من قائمة المتابعة.");
      }
    });
  }
  return (
    <div>
      <header className="hero">
        <h1>قائمة المتابعة</h1>
        <p>احفظ أزواجاً وأطراً زمنية للرجوع إليها بطلب منك.</p>
      </header>
      <aside className="demo-notice" aria-label="حدود قائمة المتابعة">
        لا تُجري القائمة تحليلاً أو مسحاً تلقائياً ولا ترسل تنبيهات أو تعرض أسعاراً حية.
        تتطلب جلسة موثوقة وسياسات مفعّلة؛ موفّر تسجيل الدخول غير مفعّل في هذه النسخة.
      </aside>
      <form className="input-panel panel" onSubmit={save} aria-busy={busy}>
        <label>
          زوج العملات
          <input
            dir="ltr"
            required
            maxLength={32}
            pattern="[A-Z0-9]+-[A-Z0-9]+"
            value={pair}
            onChange={(event) => setPair(event.target.value.toUpperCase())}
            disabled={busy}
          />
        </label>
        <label>
          الإطار الزمني
          <select
            value={timeframe}
            disabled={busy}
            onChange={(event) => setTimeframe(event.target.value as Timeframe)}
          >
            <option value="1m">دقيقة</option>
            <option value="5m">خمس دقائق</option>
            <option value="15m">خمس عشرة دقيقة</option>
            <option value="1h">ساعة</option>
            <option value="4h">أربع ساعات</option>
            <option value="1d">يوم</option>
          </select>
        </label>
        <button disabled={busy} type="submit">
          حفظ في قائمة المتابعة
        </button>
      </form>
      <div className="my-6 flex flex-wrap gap-4">
        <button disabled={busy} onClick={() => void load()}>
          تحميل قائمة المتابعة
        </button>
        {page?.next_cursor && (
          <button
            disabled={busy}
            onClick={() => void load(page.next_cursor ?? undefined)}
          >
            الصفحة التالية
          </button>
        )}
      </div>
      {busy && <p role="status">جارٍ تنفيذ طلب القائمة…</p>}
      {notice && <p role="status">{notice}</p>}
      {error && (
        <p role="alert" className="error-panel">
          {error}
        </p>
      )}
      {!busy && !error && !page && <p>حمّل القائمة لعرض العناصر المتاحة.</p>}
      {page && !busy && !error && (
        <section className="panel" aria-label="عناصر قائمة المتابعة">
          {page.items.length === 0 ? (
            <p>لا توجد عناصر متاحة في هذه الصفحة.</p>
          ) : (
            <ul className="space-y-4">
              {page.items.map((item) => (
                <li key={item.id}>
                  <h2 dir="ltr">
                    {item.pair} · {item.timeframe}
                  </h2>
                  <p>
                    انتهاء الاحتفاظ{" "}
                    <time dir="ltr" dateTime={item.expires_at}>
                      {formatUtcTimestamp(item.expires_at)}
                    </time>
                  </p>
                  <Link
                    to={`/?${new URLSearchParams({ pair: item.pair, timeframe: item.timeframe })}`}
                  >
                    اختيار {item.pair} للتحليل التجريبي
                  </Link>{" "}
                  <button
                    disabled={busy}
                    onClick={() => setPendingDelete(item)}
                    aria-label={`إزالة ${item.pair}`}
                  >
                    إزالة العنصر
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
      {pendingDelete && !busy && (
        <section className="panel" aria-label="تأكيد إزالة العنصر">
          <h2>إزالة {pendingDelete.pair} من القائمة؟</h2>
          <p>هذا لا يحذف سجل التحليلات أو الحساب. يُحفظ إجراء التدقيق بصورة مستقلة.</p>
          <button onClick={() => void remove(pendingDelete)}>تأكيد الإزالة</button>
          <button onClick={() => setPendingDelete(null)}>إلغاء</button>
        </section>
      )}
    </div>
  );
}
