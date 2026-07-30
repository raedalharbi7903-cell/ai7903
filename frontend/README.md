# Frontend

The frontend is the React application for the AI Trading Platform. Sprint 1B establishes its tooling, routing, layout, and folder conventions only; it does not include product features or API integration.

## Architecture

- `src/app`: application-level configuration.
- `src/components`: shared presentational components.
- `src/features`: feature-scoped modules as the product grows.
- `src/layouts`: reusable page shells.
- `src/pages`: route-level page components.
- `src/router`: route definitions.
- `src/services`: client-side service modules.
- `src/styles`: global style entry points.
- `src/types`, `src/hooks`, and `src/utils`: shared TypeScript types and helpers.

Empty directories are retained to make the intended application boundaries explicit.

## Commands

```bash
pnpm install
pnpm dev
pnpm build
pnpm lint
pnpm format:check
```

Copy `.env.example` to `.env` to define browser-safe variables prefixed with `VITE_`.
