# Verification and container runbook

Version 1.0 — 2026-10-29 — Engineering.

## Full local verification

From the repository root run:

```text
backend/.venv/Scripts/python scripts/verify.py
backend/.venv/Scripts/python -m unittest discover -s scripts -p test_verify.py
```

On Unix use backend/.venv/bin/python. Override --python or --pnpm to select
installed runtimes. Python 3.12, backend development dependencies, Node 24.14+
and pnpm 11.25 are prerequisites. The runner never installs Python dependencies,
changes global settings, merges, pushes or calls market providers.

The runner executes all gates even after a failure, exits nonzero on any failure,
and writes individual command/exit/output evidence under .verification (Git-ignored).
It uses test settings and starts an isolated loopback API via frontend test setup.
Each gate has a ten-minute deadline. Missing tools and deadlines are explicit
failures, not skips. Inspect output before classifying environment vs project issues.

## Container boundary

The backend image installs pinned application dependencies and runs under the
unprivileged app account. Its health check requests /health internally.
The build context excludes environments, caches, tests and environment files.
Runtime settings must be supplied externally; do not bake credentials into images.

```text
docker build -t ai-analysis-backend:local backend
docker run --rm --env-file .env -p 127.0.0.1:8000:8000 ai-analysis-backend:local
```

These are documented commands, not evidence of successful Docker execution.
The local environment has no Docker executable. Container build/start, image
security scanning, production database migrations and restore drills remain
unverified. No deployment provider or backup platform is invented here.

APP_ENVIRONMENT=production deliberately disables the unauthenticated fixture
analysis endpoint. Do not change that setting to bypass production access controls.
Health is liveness, not proof of data-provider rights, database readiness or full
product readiness. Public deployment must wait for the unresolved controls in
PROJECT_SPEC.md.
