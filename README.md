# AI Trading Platform

Production-grade backend foundation for an AI technical-analysis platform. Sprint 1A provides repository bootstrap, health checks, configuration, database scaffolding, logging, error handling, and quality tooling. Trading and AI capabilities are out of scope.

## Requirements

- Python 3.12
- pip

## Installation

Copy `.env.example` to `.env`, create and activate a Python virtual environment, then run:

```bash
make install
```

## Run locally

```bash
make run
```

Verify the service:

```bash
curl http://127.0.0.1:8000/health
```

Expected response: `{"status":"healthy"}`.

## Tests and quality checks

```bash
make test
make lint
make check-format
```

## Database migrations

Set `DATABASE_URL` in `.env`, then run `make migrate`. The initial migration only establishes Alembic version tracking; it creates no business tables.

