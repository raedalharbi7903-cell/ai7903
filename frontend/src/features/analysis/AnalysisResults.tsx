import type { AnalysisResult, Decision } from "../../types/analysis";
import { Facts, label, Panel } from "../../components/Panel";
export const decisionLabels: Record<Decision, string> = {
  buy: "BUY",
  sell: "SELL",
  no_trade: "NO TRADE",
  wait: "WAIT",
  insufficient_data: "INSUFFICIENT DATA",
};
export function AnalysisResults({ result }: { result: AnalysisResult }) {
  const output = (name: string) =>
    result.outputs.find((item) => item.engine_name === name);
  const evidence = result.outputs.flatMap((item) => item.evidence);
  const warnings = [...new Set(result.outputs.flatMap((item) => item.warnings))];
  const actionable =
    result.validation === "pass" && ["buy", "sell"].includes(result.decision);
  return (
    <div className="results" aria-live="polite">
      <section className="decision-banner" aria-label="Analysis decision">
        <div>
          <p className="eyebrow">Deterministic outcome</p>
          <h2>{decisionLabels[result.decision]}</h2>
          <p>
            Validation: <strong>{result.validation.toUpperCase()}</strong>
          </p>
        </div>
        <div className="timestamp">
          <p>Analysis generated</p>
          <time dateTime={result.generated_at}>
            {new Date(result.generated_at).toLocaleString()}
          </time>
          <p>Contract {result.contract_version}</p>
        </div>
        {!actionable && <p className="safety-note">Not an actionable trade setup.</p>}
        <p className="muted">
          Spot-only analysis. No orders are executed; SELL does not authorize a short
          position.
        </p>
      </section>
      <div className="result-grid grid gap-5 md:grid-cols-2">
        <Panel title="Market context">
          <Facts data={output("market_context")?.data ?? {}} />
          {output("market_context")?.evidence.map((item) => (
            <p key={item.evidence_id}>{item.finding}</p>
          ))}
        </Panel>
        <Panel title="Analytical confidence">
          <p className="safety-note">Analytical quality — not probability of profit.</p>
          <Facts data={output("confidence")?.data ?? {}} />
          <p className="muted">
            No calibrated win-rate or financial certainty is claimed.
          </p>
        </Panel>
        <Panel title="Data quality & provenance">
          <Facts data={output("data")?.data ?? {}} />
        </Panel>
        <Panel title="Multi-timeframe alignment">
          <Facts data={output("multi_timeframe")?.data ?? {}} />
        </Panel>
      </div>
      <Panel title="Advanced analysis">
        {!result.advanced_findings.length && <p>No advanced findings available.</p>}
        <div className="advanced-grid">
          {result.advanced_findings.map((finding) => (
            <article key={finding.engine_id} className="finding">
              <div className="finding-heading">
                <h3>{label(finding.engine_id)}</h3>
                <span className="badge">{finding.status}</span>
              </div>
              <p className="classification">
                {label(finding.classification ?? "insufficient evidence")}
              </p>
              <p className="muted">
                {finding.family ?? "unassigned"} family ·{" "}
                {finding.direction ?? "contextual"}
              </p>
              <Facts data={finding.details} />
              {finding.warnings.map((warning) => (
                <p className="warning" key={warning}>
                  {warning}
                </p>
              ))}
            </article>
          ))}
        </div>
      </Panel>
      <div className="result-grid grid gap-5 md:grid-cols-2">
        <Panel title="Evidence & confluence">
          <Facts data={output("confluence")?.data ?? {}} />
          <p className="muted">
            Multiple findings in one family do not create independent votes.
          </p>
          {evidence.length ? (
            <ul className="evidence">
              {evidence.map((item) => (
                <li key={item.evidence_id}>
                  <strong>{label(item.family)}</strong> — {label(item.finding)}
                  <small>
                    {item.source_engine} ·{" "}
                    {item.independent ? "family representative" : "shared family"}
                  </small>
                </li>
              ))}
            </ul>
          ) : (
            <p>No evidence available.</p>
          )}
        </Panel>
        <Panel title="Risk & validation">
          {actionable ? (
            <Facts data={output("risk")?.data ?? {}} />
          ) : (
            <p>
              Risk levels are withheld because this result is not an actionable
              validated setup.
            </p>
          )}
          <Facts data={output("validation")?.data ?? {}} />
        </Panel>
        <Panel title="Explanation">
          <Facts data={output("explainability")?.data ?? {}} />
          <p className="muted">AI narrative availability</p>
          <Facts data={output("ai_reasoning")?.data ?? {}} />
        </Panel>
        <Panel title="Degradation warnings">
          {warnings.length ? (
            <ul className="warnings">
              {warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p>No degradation warnings reported.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
