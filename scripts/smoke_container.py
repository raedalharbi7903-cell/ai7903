"""Smoke-test the CI-built image without mounts, secrets, or public port exposure."""

import json
import re
import subprocess
import time
from itertools import product
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def docker(*arguments: str) -> str:
    return subprocess.check_output(
        ["docker", *arguments], text=True, encoding="utf-8", timeout=60
    ).strip()


def main() -> None:
    container = docker(
        "run",
        "--rm",
        "-d",
        "-p",
        "127.0.0.1::8000",
        "--health-interval=1s",
        "--health-start-period=1s",
        "-e",
        "APP_NAME=container-smoke",
        "-e",
        "APP_ENVIRONMENT=production",
        "-e",
        "LOG_LEVEL=WARNING",
        "-e",
        "DATABASE_URL=sqlite://",
        "ai-analysis-backend:ci",
    )
    if not re.fullmatch(r"[0-9a-f]{64}", container):
        raise RuntimeError("Docker did not return a valid container identity")
    try:
        address = docker("port", container, "8000/tcp")
        if not re.fullmatch(r"127\.0\.0\.1:\d+", address):
            raise RuntimeError("Container port was not bound exclusively to loopback")
        for _ in range(100):
            try:
                with urlopen(f"http://{address}/health", timeout=1) as response:
                    if json.load(response) == {"status": "healthy"}:
                        break
            except (URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("Container did not become healthy")
        uid = docker("exec", container, "id", "-u")
        if not uid.isdigit() or uid == "0":
            raise RuntimeError("Container must not execute as root")
        request = Request(
            f"http://{address}/api/v1/analysis",
            data=json.dumps({"pair": "TEST-USDT", "timeframe": "1h"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            urlopen(request, timeout=3).close()
        except HTTPError as error:
            body = json.load(error)
            if error.code != 503 or "access controls" not in body["error"]["message"]:
                raise RuntimeError("Production demo denial was not enforced") from error
        else:
            raise RuntimeError(
                "Unauthenticated production demo was unexpectedly enabled"
            )
        for path, token in product(
            ("/api/v1/history", "/api/v1/history/00000000-0000-4000-8000-000000000001"),
            ("forged-container-token", "synthetic-history-test"),
        ):
            request = Request(
                f"http://{address}{path}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Role": "founder",
                },
            )
            try:
                urlopen(request, timeout=3).close()
            except HTTPError as error:
                body = json.load(error)
                if (
                    error.code != 401
                    or body["error"]["code"] != "authentication_required"
                ):
                    raise RuntimeError(
                        "Private history did not deny unconfigured identity"
                    ) from error
            else:
                raise RuntimeError("Private history accepted forged credentials")
        # Disposable container-local database only; never a deployed/user DB.
        migration_environment = "DATABASE_URL=sqlite:////tmp/ci-migration.db"
        docker(
            "exec",
            "-e",
            migration_environment,
            container,
            "python",
            "-m",
            "alembic",
            "upgrade",
            "head",
        )
        current = docker(
            "exec",
            "-e",
            migration_environment,
            container,
            "python",
            "-m",
            "alembic",
            "current",
        )
        if "20261030_0002" not in current:
            raise RuntimeError("Packaged migration did not reach the expected revision")
        path = (
            Path(__file__).resolve().parents[1]
            / ".verification"
            / "container-smoke.json"
        )
        path.parent.mkdir(exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "health": "PASS",
                    "non_root_uid": uid,
                    "production_demo_denial": "PASS",
                    "private_history_denial": "PASS",
                    "packaged_migration": "PASS",
                    "scope": "CI container only; not hosted production acceptance",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("Container health, non-root runtime and production denial: PASS")
    finally:
        # Exact identity returned by this run; no user containers or volumes targeted.
        docker("rm", "-f", container)


if __name__ == "__main__":
    main()
