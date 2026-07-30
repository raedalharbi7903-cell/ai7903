import { Link } from 'react-router-dom';

import { GlobalLayout } from '@/layouts/GlobalLayout';

export function NotFoundPage() {
  return (
    <GlobalLayout>
      <h1 className="text-3xl font-semibold tracking-tight">Page not found</h1>
      <p className="mt-3 text-slate-300">The requested page does not exist.</p>
      <Link
        className="mt-6 inline-block text-cyan-300 hover:text-cyan-200"
        to="/"
      >
        Return home
      </Link>
    </GlobalLayout>
  );
}
