# Frontend research workspace

React + strict TypeScript + Vite, Tailwind, React Router, ESLint and Prettier.
This is a **synthetic fixture demonstration**, not live trading intelligence.
It calls the actual FastAPI analysis endpoint; no analysis response is fabricated
by the application. The selected pair only labels the example.

## Requirements and local setup

- Node 24.14 or newer; pnpm 11.25.
- Python 3.12 and the backend development dependencies for integration tests.
- Install with `pnpm install --frozen-lockfile`.
- Start the backend from `backend`: configure the root environment as described
  in the root README, then `.venv/Scripts/python -m uvicorn app.main:app --reload`.
  On Unix, use `.venv/bin/python`.
- From this directory run `pnpm dev`.

The Vite development proxy forwards `/api` to `http://127.0.0.1:8000`.
`VITE_API_BASE_URL` defaults to `/api/v1`; it is public configuration, never a
place for credentials. A deployed web server must provide same-origin API routing.
The demo endpoint is disabled when the backend environment is production; this is
not an authenticated commercial release.

## Commands

| Command             | Purpose                                        |
| ------------------- | ---------------------------------------------- |
| `pnpm dev`          | Local development                              |
| `pnpm typecheck`    | Strict TypeScript, including test contracts    |
| `pnpm lint`         | JavaScript/TypeScript and React hooks checks   |
| `pnpm format:check` | Prettier validation                            |
| `pnpm test`         | Components plus real local FastAPI integration |
| `pnpm build`        | Type checking and production bundle            |
| `pnpm peers check`  | Dependency peer compatibility                  |

Tests automatically start an isolated local backend on a free loopback port and
stop it on completion. They use an in-memory test database setting and synthetic
candles only. Override `BACKEND_PYTHON` if the backend virtual environment is
elsewhere. No provider credentials, live market requests or database migrations
are needed. A missing backend environment fails the integration gate, not a skip.

## Architecture

- `src/app`: route composition.
- `src/layouts`: shared accessible shell and navigation.
- `src/pages`: analysis interaction and not-found route.
- `src/features/analysis`: synthetic fixture construction and analysis panels.
- `src/components`: shared panels and inspection-friendly field rendering.
- `src/services`: typed request client, timeout, safe errors.
- `src/types`: request/response contracts and runtime response validation.
- `src/test`, `tests`: component helpers and backend integration lifecycle.

The UI never computes decisions, confidence, or risk. Failed validation hides risk
levels. Confidence is analytical quality, not a percentage probability of profit.
Missing higher/lower-timeframe data remains unavailable; the primary series is
not cloned into fake independent frames. SELL does not authorize a short position.

## Toolchain compatibility

Versions are pinned and locked. TypeScript 6.0.3 is used because the installed
TypeScript ESLint parser does not support TypeScript 7. Vitest 5's two-parameter
assertion interface is extended explicitly in `src/test/setup.ts`; standard
jest-dom matchers are registered directly, without skipping library type checks.

Installation follows the official [Tailwind Vite integration](https://tailwindcss.com/docs/installation/using-vite),
[React Router declarative setup](https://reactrouter.com/start/declarative/installation)
and [Vitest guide](https://vitest.dev/guide/).
