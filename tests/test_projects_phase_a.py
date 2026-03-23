"""Phase A: fachliche Projekt-Stammdaten (DB, Service, Lifecycle-Helfer)."""

from __future__ import annotations

import sqlite3

import pytest

from app.core.db.database_manager import DatabaseManager, PROJECT_UPDATE_OMIT
from app.projects.lifecycle import validate_lifecycle_status, normalize_optional_plan_date
from app.services.project_service import ProjectService


def test_lifecycle_validate_ok():
    assert validate_lifecycle_status("ACTIVE") == "active"
    assert validate_lifecycle_status("on_hold") == "on_hold"


def test_lifecycle_validate_rejects():
    with pytest.raises(ValueError):
        validate_lifecycle_status("bogus")
    with pytest.raises(ValueError):
        validate_lifecycle_status("")
    with pytest.raises(ValueError):
        validate_lifecycle_status("   ")


def test_plan_date_normalize():
    assert normalize_optional_plan_date(None) is None
    assert normalize_optional_plan_date("") is None
    assert normalize_optional_plan_date("  ") is None
    assert normalize_optional_plan_date("2024-03-01") == "2024-03-01"


def test_plan_date_invalid():
    with pytest.raises(ValueError):
        normalize_optional_plan_date("01.03.2024")
    with pytest.raises(ValueError):
        normalize_optional_plan_date("2024-13-01")
    with pytest.raises(ValueError):
        normalize_optional_plan_date("2024-02-30")


def test_migration_legacy_db_gets_phase_a_columns(tmp_path):
    p = tmp_path / "legacy_projects.db"
    conn = sqlite3.connect(str(p))
    conn.executescript(
        """
        CREATE TABLE projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO projects (name, description, status) VALUES ('Legacy', '', 'active');
        """
    )
    conn.commit()
    conn.close()

    db = DatabaseManager(str(p), ensure_default_project=False)
    row = db.get_project(1)
    assert row is not None
    assert row.get("lifecycle_status") == "active"
    assert "customer_name" in row
    assert "planned_start_date" in row


def test_create_and_roundtrip_phase_a_fields(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "a.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    pid = svc.create_project(
        "P1",
        "d",
        status="active",
        customer_name=" ACME ",
        external_reference="REF-1",
        internal_code="INT-9",
        lifecycle_status="planned",
        planned_start_date="2025-01-15",
        planned_end_date="2025-06-30",
    )
    row = db.get_project(pid)
    assert row["customer_name"] == "ACME"
    assert row["external_reference"] == "REF-1"
    assert row["internal_code"] == "INT-9"
    assert row["lifecycle_status"] == "planned"
    assert row["planned_start_date"] == "2025-01-15"
    assert row["planned_end_date"] == "2025-06-30"

    listed = db.list_projects()
    assert any(r.get("project_id") == pid and r.get("lifecycle_status") == "planned" for r in listed)


def test_update_project_omit_vs_null(tmp_path):
    db = DatabaseManager(str(tmp_path / "b.db"), ensure_default_project=False)
    pid = db.create_project("X", customer_name="K1", lifecycle_status="active")
    db.update_project(pid, customer_name=None)
    assert db.get_project(pid)["customer_name"] is None

    db.update_project(pid, customer_name="K2", lifecycle_status="on_hold")
    r = db.get_project(pid)
    assert r["customer_name"] == "K2"
    assert r["lifecycle_status"] == "on_hold"

    db.update_project(pid, name="X2", lifecycle_status=PROJECT_UPDATE_OMIT)
    r2 = db.get_project(pid)
    assert r2["name"] == "X2"
    assert r2["lifecycle_status"] == "on_hold"


def test_project_service_invalid_lifecycle(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "c.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    with pytest.raises(ValueError):
        svc.create_project("N", lifecycle_status="nope")


def test_project_service_invalid_plan_date(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "d.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    with pytest.raises(ValueError):
        svc.create_project("N", planned_start_date="31.12.2025")


def test_project_service_update_invalid_plan_date(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "f.db"), ensure_default_project=False)
    pid = db.create_project("Z")
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    with pytest.raises(ValueError):
        svc.update_project(pid, planned_end_date="not-a-date")


def test_project_service_create_normalizes_text(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "e.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    pid = svc.create_project("N", customer_name="  ", external_reference=" R ")
    row = db.get_project(pid)
    assert row["customer_name"] is None
    assert row["external_reference"] == "R"
