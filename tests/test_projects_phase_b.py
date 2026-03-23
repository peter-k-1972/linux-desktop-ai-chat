"""Phase B: Budget, Aufwand, Meilensteine."""

from __future__ import annotations

import sqlite3

import pytest

from app.core.db.database_manager import DatabaseManager
from app.projects.controlling import milestone_summary
from app.services.project_service import ProjectService


def test_b1_migration_and_roundtrip(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "b1.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    pid = svc.create_project("P", budget_amount=1000.5, budget_currency=" eur ", estimated_effort_hours=40)
    row = db.get_project(pid)
    assert row["budget_amount"] == 1000.5
    assert row["budget_currency"] == "EUR"
    assert row["estimated_effort_hours"] == 40.0

    svc.update_project(pid, budget_amount=None, budget_currency=None, estimated_effort_hours=None)
    row2 = db.get_project(pid)
    assert row2["budget_amount"] is None
    assert row2["budget_currency"] is None
    assert row2["estimated_effort_hours"] is None


def test_b1_negative_budget_rejected(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "b1n.db"), ensure_default_project=False)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    with pytest.raises(ValueError):
        svc.create_project("P", budget_amount=-1)
    pid = svc.create_project("Q")
    with pytest.raises(ValueError):
        svc.update_project(pid, budget_amount=5, estimated_effort_hours=-0.01)


def test_b2_milestone_crud(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "b2.db"), ensure_default_project=False)
    pid = db.create_project("MP")
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    mid = svc.create_project_milestone(
        pid, "M1", "2026-06-01", status="open", sort_order=0, notes="n"
    )
    rows = svc.list_project_milestones(pid)
    assert len(rows) == 1
    assert rows[0]["name"] == "M1"
    svc.update_project_milestone(
        mid, project_id=pid, name="M1b", target_date="2026-07-01", status="done", sort_order=0, notes=None
    )
    r = db.get_project_milestone(mid)
    assert r["name"] == "M1b"
    assert r["status"] == "done"
    svc.delete_project_milestone(mid, project_id=pid)
    assert svc.list_project_milestones(pid) == []


def test_b2_delete_project_removes_milestones(tmp_path):
    db = DatabaseManager(str(tmp_path / "b2d.db"), ensure_default_project=False)
    pid = db.create_project("X")
    db.create_project_milestone(pid, "M", "2026-01-01", status="open", sort_order=0, notes=None)
    assert len(db.list_project_milestones(pid)) == 1
    db.delete_project(pid)
    with sqlite3.connect(str(tmp_path / "b2d.db")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM project_milestones WHERE project_id = ?", (pid,))
        assert cur.fetchone()[0] == 0


def test_b2_invalid_milestone(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "b2i.db"), ensure_default_project=False)
    pid = db.create_project("Z")
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    with pytest.raises(ValueError):
        svc.create_project_milestone(pid, "", "2026-01-01")
    with pytest.raises(ValueError):
        svc.create_project_milestone(pid, "N", "01.01.2026")
    with pytest.raises(ValueError):
        svc.create_project_milestone(pid, "N", "2026-01-01", status="bogus")


def test_milestone_summary_overdue():
    ms = [
        {"milestone_id": 1, "name": "A", "target_date": "2020-01-01", "status": "open"},
        {"milestone_id": 2, "name": "B", "target_date": "2030-01-01", "status": "open"},
        {"milestone_id": 3, "name": "C", "target_date": "2019-01-01", "status": "done"},
    ]
    s = milestone_summary(ms)
    assert s["open_count"] == 2
    assert s["overdue_count"] == 1
    assert s["next_milestone"]["name"] == "A"


def test_set_milestone_sort_order(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "sort.db"), ensure_default_project=False)
    pid = db.create_project("S")
    m1 = db.create_project_milestone(pid, "a", "2026-01-01", sort_order=0)
    m2 = db.create_project_milestone(pid, "b", "2026-02-01", sort_order=1)
    fake_infra = type("I", (), {"database": db})()
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)
    svc = ProjectService()
    svc.set_project_milestones_sort_order(pid, [m2, m1])
    rows = db.list_project_milestones(pid)
    assert [r["milestone_id"] for r in rows] == [m2, m1]
    assert rows[0]["sort_order"] == 0
    assert rows[1]["sort_order"] == 1
