import { appName } from '@/app/env';
import { GlobalLayout } from '@/layouts/GlobalLayout';

export function HomePage() {
  return (
    <GlobalLayout>
      <h1 className="text-3xl font-semibold tracking-tight">{appName}</h1>
      <p className="mt-3 text-slate-300">Frontend foundation is ready.</p>
    </GlobalLayout>
  );
}
