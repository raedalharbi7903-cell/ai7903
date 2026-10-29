import type { ReactNode } from "react";
export function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="panel" aria-label={title}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
export function label(value: string) {
  return value.replaceAll("_", " ");
}
export function Facts({ data }: { data: Record<string, unknown> }) {
  if (!Object.keys(data).length) return <p className="muted">Not available.</p>;
  return (
    <dl className="facts">
      {Object.entries(data).map(([key, value]) => (
        <div key={key}>
          <dt>{label(key)}</dt>
          <dd>
            {value === null || value === undefined ? (
              "Not available"
            ) : typeof value === "object" ? (
              <details>
                <summary>View details</summary>
                <pre>{JSON.stringify(value, null, 2)}</pre>
              </details>
            ) : (
              String(value)
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}
