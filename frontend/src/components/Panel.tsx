import type { ReactNode } from "react";
import { analysisLabel, analysisValue, ar } from "../i18n/ar";
export function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="panel" aria-label={title}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
export function label(value: string) {
  return analysisLabel(value);
}
export function Facts({ data }: { data: Record<string, unknown> }) {
  if (!Object.keys(data).length) return <p className="muted">{ar.notAvailable}.</p>;
  return (
    <dl className="facts">
      {Object.entries(data).map(([key, value]) => (
        <div key={key}>
          <dt>{label(key)}</dt>
          <dd>
            {value === null || value === undefined ? (
              ar.notAvailable
            ) : typeof value === "object" ? (
              <details>
                <summary>{ar.details}</summary>
                <pre dir="ltr">{JSON.stringify(value, null, 2)}</pre>
              </details>
            ) : (
              <bdi>{analysisValue(key, value)}</bdi>
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}
