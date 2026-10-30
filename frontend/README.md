# Frontend research workspace

## Private watchlist workflow

`/watchlist` has explicit load/save/delete actions with owner-scoped API storage,
typed responses, safe errors and deletion confirmation. It never scans, retrieves
prices or runs analysis automatically. A selected preference only prefills the
existing synthetic analysis form; all six supported timeframes remain labeled
as synthetic. Actual identity/retention/privacy policies are still release gates.
No demo token or mock login is built into application source.
See [watchlist contracts and limits](../docs/04-architecture/watchlist-foundation.md).

React + strict TypeScript + Vite, Tailwind, React Router, ESLint and Prettier.
This is a **synthetic fixture demonstration**, not live trading intelligence.
It calls the actual FastAPI analysis endpoint; no analysis response is fabricated
by the application. The selected pair only labels the example.

The functional shell/forms/panels are Arabic-first and RTL. Pair input and raw JSON
remain LTR; source IDs are preserved. Unknown engine observations/warnings can
remain original technical text. This is not full Arabic narrative or final design.
Copy lives in `src/i18n/ar.ts`; all ten visual categories remain pending approval.
Client HTTP/network/invalid-response errors are normalized without exposing raw
provider/body/exception text. See
[Arabic foundation and limits](../docs/03-engineering/arabic-functional-foundation.md).

## Requirements and local setup

- Node 24.14 or newer; pnpm 11.25.
- Python 3.12 and the backend development dependencies for integration tests.
- Install with `pnpm install --frozen-lockfile`.
- Start the backend from `backend`: configure the root environment as described
  in the root README, then `.venv/Scripts/python -m uvicorn app.main:app --reload --no-access-log`.
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

Private read workflow: `/history` lists saved header metadata and opens an original
stored analysis only after explicit action. It calls the actual protected GET API;
the default unconfigured identity returns 401, not fake records/login. No public
save/delete route or automatic analysis storage exists yet. History remains behind
explicit retention/privacy/identity release gates. Shared transport uses same-origin
credentials, no-store, bounded timeout and cancellation; no token in localStorage.
Tests add a separate test-only loopback HTTP server with synthetic trusted identity
and genuine pipeline snapshots, never a production auth bypass or a vendor proof.

Public functional routes: `/welcome` (product introduction), `/product` (method
and limitations), `/help` (usage guidance). Existing `/` remains the explicit
synthetic analysis interaction; unknown routes remain 404. Public pages make no
API requests, collect no customer information and do not simulate account/support
submission. They disclose that licensed live data/accounts/billing are unavailable.
Final entry-route/visual/copy/browser acceptance remains founder-gated.

Visual identity is **provisional, not founder-approved**. Existing demo colors,
font stack and color-scheme are centralized in `src/styles/tokens.css`;
`src/design/approval.ts` records the ten pending approval categories.
No Arabic font or final theme strategy is selected. See the
[design approval boundary](../docs/03-engineering/founder-design-approval.md).

- `src/app`: route composition.
- `src/layouts`: shared accessible shell and navigation.
- `src/pages`: analysis, public Arabic guidance and not-found routes.
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
