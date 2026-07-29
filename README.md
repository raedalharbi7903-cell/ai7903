# AI Trading Platform

The AI Trading Platform is a production-grade AI technical-analysis platform. This repository currently provides the Sprint 1A backend foundation: service bootstrapping, configuration, database scaffolding, structured logging, centralized error handling, and quality tooling. Trading, AI, authentication, and frontend features are intentionally not implemented yet.

## Architecture overview

The platform is organized as a monorepo with independent areas for the backend service, future frontend, database assets, deployment materials, and project documentation. The backend follows a layered FastAPI structure:

- `api` exposes HTTP routes and response contracts.
- `config` loads validated runtime configuration from environment variables.
- `core` provides cross-cutting concerns such as exception handling.
- `database` contains SQLAlchemy and Alembic infrastructure.
- `models`, `schemas`, `services`, and `dependencies` provide clear homes for future domain work.

The current public API is `GET /health`, which returns `{"status":"healthy"}`. Database infrastructure is prepared but no business tables exist in Sprint 1A.

## Repository structure

```text
ai-trading-platform/
├── backend/       FastAPI service, tests, migrations, and Dockerfile
├── frontend/      Reserved for the future frontend application
├── database/      Reserved for shared database assets
├── docker/        Reserved for container and deployment assets
├── docs/          Project, architecture, and operational documentation
├── scripts/       Project automation scripts
├── .github/       GitHub-specific configuration
├── .env.example   Environment variable template
├── Makefile       Common development commands
└── README.md      Project entry point
```

## Requirements

- Python 3.12
- pip
- GNU Make, or the equivalent commands for your environment

## Local setup

1. Copy `.env.example` to `.env` and review the environment values.
2. Create and activate a Python 3.12 virtual environment.
3. Install development dependencies:

   ```bash
   make install
   ```

4. Start the API:

   ```bash
   make run
   ```

5. Verify the health endpoint:

   ```bash
   curl http://127.0.0.1:8000/health
   ```

On Windows, activate a virtual environment with `.venv\\Scripts\\Activate.ps1`. If Make is unavailable, run the equivalent commands from the `Makefile` directly.

## Development workflow

Use the following checks before committing backend changes:

```bash
make test
make lint
make check-format
```

Use `make format` to apply Black formatting. Database changes must be represented through Alembic migrations; apply the current migration set with `make migrate` after setting `DATABASE_URL` in `.env`.

## Sprint development

Development proceeds in approved sprints. Each sprint has a defined scope and must not introduce work assigned to later sprints. Complete the specified work, validate it, document material decisions, and obtain CTO approval before beginning the next sprint. Sprint 1A is complete and establishes the baseline for subsequent backend work.

## Documentation

See [docs/README.md](docs/README.md) for the documentation scope and maintenance philosophy.
