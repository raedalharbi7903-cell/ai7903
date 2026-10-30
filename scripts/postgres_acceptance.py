"""Own a disposable loopback-only PostgreSQL server; never use DATABASE_URL."""

import json
import os
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import URL

ROOT = Path(__file__).resolve().parents[1]
IMAGE = (
    "postgres:17.11-bookworm@sha256:"
    "839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5"
)


def docker(*arguments: str, environment: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["docker", *arguments],
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    if result.returncode:
        message = result.stderr
        if environment and environment.get("POSTGRES_PASSWORD"):
            message = message.replace(environment["POSTGRES_PASSWORD"], "[redacted]")
        raise RuntimeError(f"Docker {arguments[0]} failed: {message.strip()}")
    return result.stdout.strip()


def run_backend_tests(url: str, container: str, password: str) -> str:
    environment = {
        **os.environ,
        "APP_NAME": "postgres-acceptance",
        "APP_ENVIRONMENT": "testing",
        "LOG_LEVEL": "WARNING",
        "DATABASE_URL": url,
        "POSTGRES_ACCEPTANCE_OWNED_CONTAINER": container,
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "integration/test_postgres.py",
            "-o",
            f"cache_dir={ROOT / '.verification' / 'postgres-pytest-cache'}",
        ],
        cwd=ROOT / "backend",
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    output = (result.stdout + result.stderr).replace(password, "[redacted]")
    if result.returncode:
        raise RuntimeError(f"PostgreSQL integration failed:\n{output}")
    return output


def verify_recovery(container: str, database: str) -> None:
    def sql(db: str, statement: str) -> str:
        return docker(
            "exec",
            container,
            "psql",
            "-U",
            "ci_owner",
            "-d",
            db,
            "-v",
            "ON_ERROR_STOP=1",
            "-Atc",
            statement,
        )

    sql(
        database,
        "CREATE TABLE recovery_probe (value text NOT NULL); "
        "INSERT INTO recovery_probe VALUES ('synthetic-recovery');",
    )
    docker(
        "exec",
        container,
        "pg_dump",
        "-U",
        "ci_owner",
        "-d",
        database,
        "-Fc",
        "-f",
        "/tmp/acceptance.dump",
    )
    sql(database, "UPDATE recovery_probe SET value = 'changed-after-backup'")
    restored = database + "_restored"
    docker("exec", container, "createdb", "-U", "ci_owner", restored)
    docker(
        "exec",
        container,
        "pg_restore",
        "-U",
        "ci_owner",
        "--exit-on-error",
        "-d",
        restored,
        "/tmp/acceptance.dump",
    )
    if sql(restored, "SELECT value FROM recovery_probe") != "synthetic-recovery":
        raise RuntimeError("PostgreSQL restored snapshot did not retain backup state")
    if sql(restored, "SELECT version_num FROM alembic_version") != "20260725_0001":
        raise RuntimeError("PostgreSQL restored migration revision did not match")


def _run() -> dict:
    password = secrets.token_urlsafe(32)
    database = "ai_ci_" + secrets.token_hex(8)
    environment = {**os.environ, "POSTGRES_PASSWORD": password}
    container = docker(
        "run",
        "-d",
        "--memory=512m",
        "--cpus=1",
        "-p",
        "127.0.0.1::5432",
        "--tmpfs",
        "/var/lib/postgresql/data:rw,nosuid,nodev,size=256m",
        "-e",
        "POSTGRES_PASSWORD",
        "-e",
        "POSTGRES_USER=ci_owner",
        "-e",
        f"POSTGRES_DB={database}",
        IMAGE,
        environment=environment,
    )
    if not re.fullmatch(r"[0-9a-f]{64}", container):
        raise RuntimeError("Docker did not return a valid owned container identity")
    try:
        address = docker("port", container, "5432/tcp")
        if not re.fullmatch(r"127\.0\.0\.1:\d+", address):
            raise RuntimeError("PostgreSQL must be bound exclusively to loopback")
        port = int(address.rsplit(":", 1)[1])
        if not 1 <= port <= 65535:
            raise RuntimeError("Invalid PostgreSQL mapped port")
        for _ in range(50):
            try:
                # initdb's temporary Unix-socket server is not host-ready.
                docker(
                    "exec",
                    container,
                    "pg_isready",
                    "-h",
                    "127.0.0.1",
                    "-U",
                    "ci_owner",
                    "-d",
                    database,
                )
                break
            except RuntimeError:
                time.sleep(0.2)
        else:
            raise RuntimeError("Disposable PostgreSQL did not become ready")
        url = URL.create(
            "postgresql+psycopg",
            username="ci_owner",
            password=password,
            host="127.0.0.1",
            port=port,
            database=database,
            query={"connect_timeout": "3"},
        ).render_as_string(hide_password=False)
        output = run_backend_tests(url, container, password)
        verify_recovery(container, database)
        return {
            "scope": "Disposable CI PostgreSQL only, not production",
            "image": IMAGE,
            "integration_tests": "PASS",
            "backup_restore": "PASS",
            "migration_restore": "PASS",
            "loopback_only": True,
            "pytest_output": output,
        }
    finally:
        # Exact owned ID only. No host mounts or existing/user databases involved.
        docker("rm", "-f", container)


def main() -> None:
    report = ROOT / ".verification" / "postgres-acceptance.json"
    report.parent.mkdir(exist_ok=True)
    identity = {
        "scope": "Disposable CI PostgreSQL only, not production",
        "source_commit": os.environ.get("GITHUB_SHA"),
    }
    report.write_text(
        json.dumps({**identity, "status": "RUNNING"}, indent=2), encoding="utf-8"
    )
    try:
        result = _run()
    except Exception as error:
        report.write_text(
            json.dumps(
                {
                    **identity,
                    "status": (
                        "NOT VERIFIED"
                        if isinstance(error, FileNotFoundError)
                        else "FAIL"
                    ),
                    "error_category": type(error).__name__,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        raise
    report.write_text(
        json.dumps({**identity, **result, "status": "PASS"}, indent=2),
        encoding="utf-8",
    )
    print(result["pytest_output"])
    print("Disposable PostgreSQL migration/transaction/recovery acceptance: PASS")


if __name__ == "__main__":
    main()
