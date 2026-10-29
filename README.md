# AI Trading Analysis Platform

A spot-only cryptocurrency analysis research platform: deterministic observations
flow through evidence, confluence, decision, risk, confidence, validation and
explanation. React consumes the FastAPI analysis service. No automatic trading.

**Current status: incomplete product; synthetic-fixture demonstration only.**
There is no approved commercial live-data integration or configured AI narrative
provider. Confidence is uncalibrated analytical quality, not probability of profit.
The production environment disables the unauthenticated demo analysis endpoint.
See [requirements and open decisions](PROJECT_SPEC.md) and the
[requirement-to-evidence matrix](docs/10-testing/requirement-evidence-matrix.md).

## Prerequisites

Python 3.12, pip, Node 24.14+, pnpm 11.25. Docker is optional for local development;
container acceptance is a separate CI step. Never put credentials in frontend
environment variables or commit a real environment file.

## Local setup

Copy .env.example to .env and review all values. Existing provider-related example
settings do not authorize live acquisition; the analysis endpoint accepts fixtures
only and does not automatically call those providers.

Create backend/.venv with Python 3.12 and install:

```text
backend/.venv/Scripts/python -m pip install -r backend/requirements/dev.txt
```

On Unix substitute backend/.venv/bin/python. From backend/ start:

```text
.venv/Scripts/python -m uvicorn app.main:app --reload
```

From frontend/ run pnpm install --frozen-lockfile, then pnpm dev. The development
proxy forwards /api to 127.0.0.1:8000. GET /health returns {"status":"healthy"}.
Frontend setup, demo limits and commands are in [frontend/README.md](frontend/README.md).

## Repository and architecture

- backend/app: API, application services, sequential analysis pipeline, models,
  configuration, database/repository foundation, logging and error boundaries.
- backend/tests: infrastructure, engine behavior, historical safety and API tests.
- frontend/src: routed pages, layouts, reusable components, analysis experience,
  typed API client and runtime response validation.
- backend/alembic: schema migration foundation; no business tables yet.
- docs: governance, product, engineering, architecture and operational evidence.
- scripts: full verification, documentation audit, synthetic latency measurement
  and isolated CI container smoke testing.
- .github/workflows: pinned, read-only CI; no deployment or merge automation.

## Verification workflow

From the root:

```text
backend/.venv/Scripts/python scripts/verify.py
```

The runner executes all 17 gates, records outputs/statuses under .verification,
and exits nonzero if any required gate fails. Frontend integration tests start the
actual backend on an isolated loopback port. No market provider is contacted.
See the [verification runbook](docs/09-devops/verification-runbook.md).
Hosted CI status must be inspected independently; local passing tests do not
prove Linux or production readiness.

For database migrations, configure DATABASE_URL in .env and run python -m alembic
upgrade head from backend/ using the virtual environment. The initial migration
only establishes Alembic version tracking.

## Delivery and sprint workflow

Work only on feature/crypto-analysis-validation. Preserve unrelated edits, verify
coherent packages, update PROGRESS.md, commit and push the feature branch. Never
merge or push main. CTO approval is required before a new sprint or unresolved
product/architecture decisions. Do not declare completion until every agreed
requirement has adequate implementation and verification evidence.

The original Sprint 1A foundation remains preserved; its health/database/logging
scaffolding has been extended by later approved analysis and frontend work.

