import { Link, Outlet } from "react-router";
import { visualApproval } from "../design/approval";
import { ar } from "../i18n/ar";
export function Layout() {
  return (
    <div lang="ar" dir="rtl">
      <a className="skip-link" href="#content">
        {ar.skip}
      </a>
      <nav className="topbar flex-wrap" aria-label={ar.navigation}>
        <Link to="/" className="brand">
          A / I <span>ANALYSIS</span>
        </Link>
        <div className="flex flex-wrap items-center gap-4">
          <Link to="/welcome">تعريف المنصة</Link>
          <Link to="/product">منهج التحليل</Link>
          <Link to="/help">المساعدة</Link>
          <Link to="/">التحليل التجريبي</Link>
        </div>
        <span className="badge">{ar.workspace}</span>
      </nav>
      <main id="content" tabIndex={-1}>
        <Outlet />
      </main>
      <footer>
        {ar.footer}
        {visualApproval.status === "pending" && <p>{ar.designPending}</p>}
      </footer>
    </div>
  );
}
