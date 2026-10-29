import { Link } from "react-router";
export function NotFoundPage() {
  return (
    <section className="panel">
      <h1>Page not found</h1>
      <Link to="/">Return to analysis</Link>
    </section>
  );
}
