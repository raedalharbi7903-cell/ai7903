import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import URL

BACKEND = Path(__file__).resolve().parents[1]


def migrate(database: Path, *arguments: str) -> subprocess.CompletedProcess:
    environment = {
        **os.environ,
        "APP_NAME": "migration-test",
        "APP_ENVIRONMENT": "testing",
        "LOG_LEVEL": "WARNING",
        "DATABASE_URL": URL.create("sqlite", database=str(database)).render_as_string(
            hide_password=False
        ),
    }
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND,
        env=environment,
        text=True,
        capture_output=True,
        timeout=30,
    )


@pytest.mark.parametrize("name", ["roundtrip.db", "roundtrip%25.db"])
def test_initial_migration_up_down_roundtrip(tmp_path, name) -> None:
    database = tmp_path / name
    upgrade = migrate(database, "upgrade", "20260725_0001")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(database) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert tables == [("alembic_version",)]
        assert connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone() == ("20260725_0001",)
    current = migrate(database, "current")
    assert current.returncode == 0, current.stderr
    assert "20260725_0001" in current.stdout
    downgrade = migrate(database, "downgrade", "base")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute("SELECT version_num FROM alembic_version").fetchall()
            == []
        )


def test_sqlite_backup_restores_committed_revision_and_synthetic_probe(
    tmp_path,
) -> None:
    source = tmp_path / "source.db"
    backup = tmp_path / "backup.db"
    restored = tmp_path / "restored.db"
    upgrade = migrate(source, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(source) as database:
        # Disposable recovery probe only; not an application/business schema.
        database.execute("CREATE TABLE recovery_probe (value TEXT NOT NULL)")
        database.execute("INSERT INTO recovery_probe VALUES ('synthetic-recovery')")
    with sqlite3.connect(source) as database, sqlite3.connect(backup) as destination:
        database.backup(destination)
    # Modify the original after backup to verify snapshot consistency.
    with sqlite3.connect(source) as database:
        database.execute("DELETE FROM recovery_probe")
    with sqlite3.connect(backup) as database, sqlite3.connect(restored) as destination:
        database.backup(destination)
    with sqlite3.connect(restored) as database:
        assert database.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert database.execute("SELECT value FROM recovery_probe").fetchall() == [
            ("synthetic-recovery",)
        ]
        assert database.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone() == ("20261030_0004",)
    current = migrate(restored, "current")
    assert current.returncode == 0, current.stderr
    assert "20261030_0004" in current.stdout


def test_audit_migration_preserves_existing_history_revision_data(tmp_path) -> None:
    database = tmp_path / "audit-upgrade.db"
    result = migrate(database, "upgrade", "20261030_0002")
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(database) as connection:
        assert not connection.execute(
            "SELECT name FROM sqlite_master WHERE name='audit_events'"
        ).fetchall()
        # Synthetic storage probe only; never presented as an analytical result.
        connection.execute(
            "INSERT INTO analysis_history VALUES (?, ?, ?, ?, ?, ?)",
            (
                "00000000-0000-4000-8000-000000000001",
                "a" * 64,
                "2026-01-01 00:00:00",
                "2026-01-02 00:00:00",
                "synthetic-migration-only",
                "synthetic-preservation-probe",
            ),
        )
    upgrade = migrate(database, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT result_json FROM analysis_history"
        ).fetchall() == [("synthetic-preservation-probe",)]
        assert connection.execute("SELECT count(*) FROM audit_events").fetchone() == (
            0,
        )
    downgrade = migrate(database, "downgrade", "20261030_0002")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT result_json FROM analysis_history"
        ).fetchall() == [("synthetic-preservation-probe",)]
        assert not connection.execute(
            "SELECT name FROM sqlite_master WHERE name='audit_events'"
        ).fetchall()


def test_offline_migration_does_not_connect_or_create_database(tmp_path) -> None:
    database = tmp_path / "offline%25.db"
    result = migrate(database, "upgrade", "head", "--sql")
    assert result.returncode == 0, result.stderr
    assert "alembic_version" in result.stdout
    assert "20260725_0001" in result.stdout
    assert "20261030_0002" in result.stdout
    assert "20261030_0003" in result.stdout
    assert "20261030_0004" in result.stdout
    assert "watchlist" in result.stdout
    assert "audit_events" in result.stdout
    assert "analysis_history" in result.stdout
    assert not database.exists()


def test_history_head_schema_roundtrip_and_initial_revision_preserved(tmp_path) -> None:
    database = tmp_path / "history.db"
    upgrade = migrate(database, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone() == ("20261030_0004",)
        assert connection.execute("PRAGMA table_info(audit_events)").fetchall()
        columns = connection.execute("PRAGMA table_info(analysis_history)").fetchall()
        assert [column[1] for column in columns] == [
            "id",
            "owner_key",
            "created_at",
            "expires_at",
            "policy_reference",
            "result_json",
        ]
        indexes = connection.execute("PRAGMA index_list(analysis_history)").fetchall()
        assert {"ix_analysis_history_owner_page", "ix_analysis_history_expiry"} <= {
            index[1] for index in indexes
        }
    downgrade = migrate(database, "downgrade", "20260725_0001")
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall() == [("alembic_version",)]
    assert migrate(database, "upgrade", "head").returncode == 0
