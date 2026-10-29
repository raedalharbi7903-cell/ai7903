import { useState } from "react";
import type { FormEvent } from "react";
import { requestAnalysis } from "../services/analysis";
import { createFixture } from "../features/analysis/fixture";
import { AnalysisResults } from "../features/analysis/AnalysisResults";
import type { AnalysisResult, Timeframe } from "../types/analysis";
export function AnalysisPage() {
  const [pair, setPair] = useState("TEST-USDT");
  const [timeframe, setTimeframe] = useState<Timeframe>("1h");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await requestAnalysis(createFixture(pair, timeframe)));
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Analysis failed. Please retry.",
      );
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <header className="hero">
        <p className="eyebrow">CRYPTO / SPOT / RESEARCH</p>
        <h1>Evidence before conviction.</h1>
        <p>Inspect the structure. Understand the uncertainty.</p>
      </header>
      <aside className="demo-notice" aria-label="Demo limitations">
        <strong>DEMO MODE — synthetic fixtures only</strong>
        <p>
          No live prices or market intelligence. Pair names label a synthetic example,
          not actual market history. Independent higher/lower timeframe data is not
          supplied; missing confirmation is shown explicitly.
        </p>
      </aside>
      <form className="input-panel panel" onSubmit={submit} aria-busy={loading}>
        <label>
          Trading pair
          <input
            required
            maxLength={32}
            pattern="[A-Z0-9]+-[A-Z0-9]+"
            value={pair}
            disabled={loading}
            onChange={(event) => setPair(event.target.value.toUpperCase())}
          />
        </label>
        <label>
          Primary timeframe
          <select
            value={timeframe}
            disabled={loading}
            onChange={(event) => setTimeframe(event.target.value as Timeframe)}
          >
            <option value="1h">1 hour</option>
            <option value="4h">4 hours</option>
            <option value="1d">1 day</option>
          </select>
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Analyzing…" : "Analyze fixture"}
        </button>
      </form>
      {loading && (
        <p role="status" className="empty-state">
          Running deterministic analysis…
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
            <h2>Your analysis workspace is ready.</h2>
            <p>
              Run the clearly labeled fixture to inspect evidence, safety checks and
              advanced findings.
            </p>
          </section>
        )
      )}
    </>
  );
}
