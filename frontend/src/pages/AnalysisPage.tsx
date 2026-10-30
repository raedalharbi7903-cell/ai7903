import { useState } from "react";
import type { FormEvent } from "react";
import { AnalysisClientError, requestAnalysis } from "../services/analysis";
import { requestSavedAnalysis } from "../services/history";
import { Link } from "react-router";
import { ar } from "../i18n/ar";
import { createFixture } from "../features/analysis/fixture";
import { AnalysisResults } from "../features/analysis/AnalysisResults";
import type { AnalysisResult, Timeframe } from "../types/analysis";
export function AnalysisPage() {
  const [pair, setPair] = useState("TEST-USDT");
  const [timeframe, setTimeframe] = useState<Timeframe>("1h");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setSaved(false);
    try {
      const submitter = (event.nativeEvent as SubmitEvent).submitter;
      const save = submitter instanceof HTMLButtonElement && submitter.value === "save";
      const payload = createFixture(pair, timeframe);
      if (save) {
        const entry = await requestSavedAnalysis(payload);
        setResult(entry.result);
        setSaved(true);
      } else {
        setResult(await requestAnalysis(payload));
      }
    } catch (reason) {
      setError(reason instanceof AnalysisClientError ? reason.message : ar.unavailable);
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <header className="hero">
        <p className="eyebrow">{ar.category}</p>
        <h1>{ar.heading}</h1>
        <p>{ar.introduction}</p>
      </header>
      <aside className="demo-notice" aria-label={ar.demoLabel}>
        <strong>{ar.demoTitle}</strong>
        <p>{ar.demoDescription}</p>
      </aside>
      <form className="input-panel panel" onSubmit={submit} aria-busy={loading}>
        <label>
          {ar.pair}
          <input
            required
            dir="ltr"
            aria-describedby="pair-hint"
            maxLength={32}
            pattern="[A-Z0-9]+-[A-Z0-9]+"
            value={pair}
            disabled={loading}
            onChange={(event) => setPair(event.target.value.toUpperCase())}
          />
        </label>
        <label>
          {ar.timeframe}
          <select
            value={timeframe}
            disabled={loading}
            onChange={(event) => setTimeframe(event.target.value as Timeframe)}
          >
            <option value="1h">{ar.hour}</option>
            <option value="4h">{ar.fourHours}</option>
            <option value="1d">{ar.day}</option>
          </select>
        </label>
        <button type="submit" value="analyze" disabled={loading}>
          {loading ? ar.analyzing : ar.analyze}
        </button>
        <button type="submit" value="save" disabled={loading}>
          تحليل جديد وحفظ النتيجة
        </button>
      </form>
      <p id="pair-hint" className="muted">
        {ar.pairHint}
      </p>
      <p className="muted">
        الحفظ إجراء صريح يتطلب جلسة موثوقة وسياسات مفعّلة؛ التحليل العادي لا يُحفظ
        تلقائياً.
      </p>
      {saved && (
        <p role="status">
          حُفظت النتيجة. <Link to="/history">افتح سجل التحليلات</Link>
        </p>
      )}
      {loading && (
        <p role="status" className="empty-state">
          {ar.progress}
        </p>
      )}
      {error && (
        <p role="alert" className="error-panel">
          {error}
        </p>
      )}
      {result ? (
        <AnalysisResults result={result} />
      ) : (
        !loading &&
        !error && (
          <section className="empty-state">
            <h2>{ar.ready}</h2>
            <p>{ar.empty}</p>
          </section>
        )
      )}
    </>
  );
}
