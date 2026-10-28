import { useState } from "react";
import { requestAnalysis } from "../services/analysis";
import type { AnalysisResult } from "../types/analysis";

const fixture = (pair: string, timeframe: string) => ({
  pair, timeframe, request_id: crypto.randomUUID(),
  market_data: { instrument: pair, market: "crypto", timeframe, provider: "demo_fixture", source_timestamp: "2026-01-01T04:00:00Z", fixture: true, candles: [10,11,12,13,14].map((close, index) => ({timestamp: `2026-01-01T0${index}:00:00Z`, open: close - 1, high: close + 1, low: close - 2, close, volume: 100 + index})) },
  metadata: { timeframes: {} }
});

export function App() {
  const [pair, setPair] = useState("TEST-USDT"); const [timeframe, setTimeframe] = useState("1h");
  const [result, setResult] = useState<AnalysisResult | null>(null); const [error, setError] = useState<string | null>(null); const [loading, setLoading] = useState(false);
  async function submit() { setLoading(true); setError(null); try { const payload = fixture(pair, timeframe); payload.metadata.timeframes = {htf: payload.market_data, itf: payload.market_data, ltf: payload.market_data}; setResult(await requestAnalysis(payload)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Analysis failed"); } finally { setLoading(false); } }
  return <main><header><p>DEMO MODE · fixture-driven analysis only</p><h1>Crypto Analysis</h1></header><section className="panel"><label>Pair<input value={pair} onChange={(event) => setPair(event.target.value.toUpperCase())} /></label><label>Timeframe<select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}><option>1h</option><option>4h</option><option>1d</option></select></label><button disabled={loading} onClick={submit}>{loading ? "Analyzing…" : "Analyze fixture"}</button>{error && <p role="alert">{error}</p>}</section>{result && <section className="panel"><h2>{result.decision.replace("_", " ")}</h2><p>Validation: {result.validation} · Generated: {new Date(result.generated_at).toLocaleString()}</p><p>Analytical confidence is not a probability of profit.</p><ul>{result.outputs.flatMap((output) => output.warnings).map((warning) => <li key={warning}>{warning}</li>)}</ul></section>}</main>;
}
