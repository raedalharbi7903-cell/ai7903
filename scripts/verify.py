"""Run reproducible repository gates; nonzero exit if any required gate fails."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def gates(root: Path, python: str, pnpm: str) -> list[tuple[str, Path, list[str]]]:
    backend, frontend = root / "backend", root / "frontend"
    return [
        (
            "tooling-tests",
            root,
            [python, "-m", "unittest", "discover", "-s", "scripts", "-p", "test_*.py"],
        ),
        ("tooling-lint", backend, [python, "-m", "ruff", "check", "../scripts"]),
        ("tooling-format", backend, [python, "-m", "black", "--check", "../scripts"]),
        ("documentation-links", root, [python, "scripts/audit_documents.py"]),
        (
            "backend-tests",
            backend,
            [
                python,
                "-m",
                "pytest",
                "-o",
                f"cache_dir={root / '.verification' / 'pytest-cache'}",
            ],
        ),
        (
            "backend-lint",
            backend,
            [python, "-m", "ruff", "check", ".", "alembic/env.py"],
        ),
        (
            "backend-format",
            backend,
            [python, "-m", "black", "--check", "app", "tests", "alembic/env.py"],
        ),
        ("backend-compile", backend, [python, "-m", "compileall", "-q", "app"]),
        (
            "backend-import",
            backend,
            [
                python,
                "-c",
                "from app.main import app; "
                "from app.analysis.service import AnalysisService; "
                "assert app and AnalysisService",
            ],
        ),
        ("backend-dependencies", backend, [python, "-m", "pip", "check"]),
        ("frontend-install", frontend, [pnpm, "install", "--frozen-lockfile"]),
        ("frontend-types", frontend, [pnpm, "typecheck"]),
        ("frontend-lint", frontend, [pnpm, "lint"]),
        ("frontend-tests", frontend, [pnpm, "test"]),
        ("frontend-format", frontend, [pnpm, "format:check"]),
        ("frontend-build", frontend, [pnpm, "build"]),
        ("frontend-peers", frontend, [pnpm, "peers", "check"]),
    ]


def run_gate(name: str, cwd: Path, command: list[str], env: dict[str, str]) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        return {
            "gate": name,
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "command": command,
            "exit_code": result.returncode,
            "output": result.stdout + result.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "gate": name,
            "status": "FAIL",
            "command": command,
            "error_category": type(error).__name__,
            "message": str(error),
        }


def main() -> int:
    # Windows terminals may default to a legacy encoding. Preserve diagnostic
    # Unicode without crashing before remaining gates and evidence are recorded.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python",
        default=str(
            root
            / "backend"
            / ".venv"
            / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        ),
    )
    parser.add_argument("--pnpm", default=shutil.which("pnpm") or "pnpm")
    args = parser.parse_args()
    env = dict(os.environ)
    env.update(
        APP_NAME="verification",
        APP_ENVIRONMENT="testing",
        LOG_LEVEL="WARNING",
        DATABASE_URL="sqlite://",
        BLACK_CACHE_DIR=str(root / "backend" / ".black-cache"),
        RUFF_CACHE_DIR=str(root / ".verification" / "ruff-cache"),
        # Resolving a POSIX venv symlink selects the base interpreter and loses
        # the venv's installed dependencies. Normalize without dereferencing.
        BACKEND_PYTHON=os.path.abspath(args.python),
    )
    results = []
    for name, cwd, command in gates(root, args.python, args.pnpm):
        result = run_gate(name, cwd, command, env)
        results.append(result)
        print(f"{name}: {result['status']}", flush=True)
        if result["status"] != "PASS":
            print(result.get("output", result.get("message", "")), flush=True)
    report = root / ".verification" / "quality-gates.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(
        json.dumps(
            {"generated_at": datetime.now(UTC).isoformat(), "results": results},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Evidence: {report}", flush=True)
    return 0 if all(r["status"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
