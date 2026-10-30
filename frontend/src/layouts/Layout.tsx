import { Link, Outlet } from "react-router";
import { visualApproval } from "../design/approval";
export function Layout() {
  return (
    <>
      <a className="skip-link" href="#content">
        Skip to analysis
      </a>
      <nav className="topbar" aria-label="Main navigation">
        <Link to="/" className="brand">
          A / I <span>ANALYSIS</span>
        </Link>
        <span className="badge">RESEARCH WORKSPACE</span>
      </nav>
      <main id="content">
        <Outlet />
      </main>
      <footer>
        Deterministic evidence. Explicit uncertainty. No automatic trading.
        {visualApproval.status === "pending" && (
          <p>Visual design is provisional and awaiting founder approval.</p>
        )}
      </footer>
    </>
  );
}
