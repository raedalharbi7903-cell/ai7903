import { Link } from "react-router";
import { ar } from "../i18n/ar";
export function NotFoundPage() {
  return (
    <section className="panel">
      <h1>{ar.missingPage}</h1>
      <Link to="/">{ar.returnToAnalysis}</Link>
    </section>
  );
}
