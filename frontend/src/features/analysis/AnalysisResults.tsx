import type { AnalysisResult, Decision } from "../../types/analysis";
import { readArabicExplanation } from "../../types/explanation";
import { ar, formatUtcTimestamp } from "../../i18n/ar";
import { Facts, label, Panel } from "../../components/Panel";
export const decisionLabels: Record<Decision, string> = {
  buy: "شراء",
  sell: "بيع",
  no_trade: "لا تداول",
  wait: "انتظار",
  insufficient_data: "بيانات غير كافية",
};
export function AnalysisResults({ result }: { result: AnalysisResult }) {
  const output = (name: string) =>
    result.outputs.find((item) => item.engine_name === name);
  const evidence = result.outputs.flatMap((item) => item.evidence);
  const warnings = [...new Set(result.outputs.flatMap((item) => item.warnings))];
  const actionable =
    result.validation === "pass" && ["buy", "sell"].includes(result.decision);
  const arabicExplanation = readArabicExplanation(result);
  return (
    <div className="results" aria-live="polite">
      <section className="decision-banner" aria-label={ar.decision}>
        <div>
          <p className="eyebrow">{ar.deterministic}</p>
          <h2>{decisionLabels[result.decision]}</h2>
          <p>
            {ar.validation}: <strong>{label(result.validation)}</strong>
          </p>
        </div>
        <div className="timestamp">
          <p>{ar.generated}</p>
          <time dateTime={result.generated_at} dir="ltr">
            {formatUtcTimestamp(result.generated_at)}
          </time>
          <p>
            {ar.contract} <bdi>{result.contract_version}</bdi>
          </p>
        </div>
        {!actionable && <p className="safety-note">{ar.notActionable}</p>}
        <p className="muted">{ar.spotOnly}</p>
      </section>
      <div className="result-grid grid gap-5 md:grid-cols-2">
        <Panel title={ar.context}>
          <Facts data={output("market_context")?.data ?? {}} />
          {output("market_context")?.evidence.map((item) => (
            <p key={item.evidence_id}>{item.finding}</p>
          ))}
        </Panel>
        <Panel title={ar.confidence}>
          <p className="safety-note">{ar.confidenceNote}</p>
          <Facts data={output("confidence")?.data ?? {}} />
          <p className="muted">{ar.calibrationNote}</p>
        </Panel>
        <Panel title={ar.provenance}>
          <Facts data={output("data")?.data ?? {}} />
        </Panel>
        <Panel title={ar.mtf}>
          <Facts data={output("multi_timeframe")?.data ?? {}} />
        </Panel>
      </div>
      <Panel title={ar.advanced}>
        {!result.advanced_findings.length && <p>{ar.noAdvanced}</p>}
        <div className="advanced-grid">
          {result.advanced_findings.map((finding) => (
            <article key={finding.engine_id} className="finding">
              <div className="finding-heading">
                <h3>{label(finding.engine_id)}</h3>
                <span className="badge">{label(finding.status)}</span>
              </div>
              <p className="classification">
                {label(finding.classification ?? "insufficient evidence")}
              </p>
              <p className="muted">
                {ar.family} {label(finding.family ?? "unassigned")} ·{" "}
                {finding.direction ? label(finding.direction) : ar.contextual}
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
        <Panel title={ar.evidence}>
          <Facts data={output("confluence")?.data ?? {}} />
          <p className="muted">{ar.independence}</p>
          {evidence.length ? (
            <ul className="evidence">
              {evidence.map((item) => (
                <li key={item.evidence_id}>
                  <strong>{label(item.family)}</strong> — <bdi>{item.finding}</bdi>
                  <small>
                    {item.source_engine} ·{" "}
                    {item.independent ? ar.representative : ar.shared}
                    {" · "}
                    {item.bias === "bullish" || item.bias === "bearish"
                      ? label(item.bias)
                      : ar.nonDirectional}
                  </small>
                </li>
              ))}
            </ul>
          ) : (
            <p>{ar.noEvidence}</p>
          )}
        </Panel>
        <Panel title={ar.risk}>
          {actionable ? (
            <Facts data={output("risk")?.data ?? {}} />
          ) : (
            <p>{ar.withheldRisk}</p>
          )}
          <Facts data={output("validation")?.data ?? {}} />
        </Panel>
        <Panel title={ar.explanation}>
          {arabicExplanation ? (
            <div lang="ar" dir="rtl">
              <p>{arabicExplanation.summary}</p>
              <ul>
                {arabicExplanation.limitations.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </div>
          ) : output("explainability")?.data.arabic_explanation !== undefined ? (
            <p>{ar.noTrustedExplanation}</p>
          ) : (
            <Facts data={output("explainability")?.data ?? {}} />
          )}
          <p className="muted">{ar.aiAvailability}</p>
          <Facts data={output("ai_reasoning")?.data ?? {}} />
        </Panel>
        <Panel title={ar.warnings}>
          {warnings.length ? (
            <ul className="warnings">
              {warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p>{ar.noWarnings}</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
