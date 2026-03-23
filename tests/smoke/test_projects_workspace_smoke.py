"""
Smoke Tests: Projects-Workspace (Persistenz & kritische Texte).

Keine Qt-Bot-Automatisierung: DB, ProjectService mit injizierter DB, Import/Instanzierung
des Workspaces. Manuelle UI-Prüfungen: docs/QA_PROJECTS_WORKSPACE_CHECKLIST.md
"""

from __future__ import annotations

import types

import pytest

from app.core.db.database_manager import DatabaseManager
from app.gui.domains.operations.projects.projects_workspace import NewProjectDialog


@pytest.mark.smoke
def test_smoke_create_project_appears_in_list(tmp_path):
    """Projekt anlegen → list_projects enthält es."""
    db_path = str(tmp_path / "projects_smoke.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("Smoke-Projekt", description="d", status="active")
    rows = db.list_projects()
    hit = next(r for r in rows if r.get("project_id") == pid)
    assert hit.get("name") == "Smoke-Projekt"
    assert hit.get("lifecycle_status") == "active"


@pytest.mark.smoke
def test_smoke_update_project_policy_visible_in_get(tmp_path):
    """update_project setzt Policy; get_project liefert sie."""
    db_path = str(tmp_path / "projects_policy.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("P")
    db.update_project(pid, default_context_policy="debug")
    row = db.get_project(pid)
    assert row is not None
    assert row.get("default_context_policy") == "debug"


@pytest.mark.smoke
def test_smoke_clear_default_context_policy_null(tmp_path):
    """App-Standard: default_context_policy in DB = NULL."""
    db_path = str(tmp_path / "projects_null_pol.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("P", default_context_policy="architecture")
    assert db.get_project(pid).get("default_context_policy") == "architecture"
    db.update_project(pid, clear_default_context_policy=True)
    assert db.get_project(pid).get("default_context_policy") is None


@pytest.mark.smoke
def test_smoke_delete_project_removed_from_list(tmp_path):
    """delete_project → Projekt nicht mehr in list_projects."""
    db_path = str(tmp_path / "projects_del.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("Weg")
    db.delete_project(pid)
    rows = db.list_projects()
    assert not any(r.get("project_id") == pid for r in rows)


@pytest.mark.smoke
def test_smoke_list_projects_includes_default_context_policy(tmp_path):
    """Liste enthält default_context_policy (Overview/Liste konsistent nach Edit)."""
    db_path = str(tmp_path / "projects_list_pol.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("Q", default_context_policy="default")
    listed = db.list_projects()
    hit = next(r for r in listed if r.get("project_id") == pid)
    assert hit.get("default_context_policy") == "default"


@pytest.mark.smoke
def test_smoke_project_service_create_update_delete(tmp_path, monkeypatch):
    """ProjectService delegiert auf dieselbe DB (Workspace-Pfad)."""
    db = DatabaseManager(str(tmp_path / "psvc.db"), ensure_default_project=False)
    fake_infra = types.SimpleNamespace(database=db)
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake_infra)

    from app.services.project_service import ProjectService

    svc = ProjectService()
    pid = svc.create_project("SvcSmoke", "desc", status="archived")
    svc.update_project(pid, name="SvcSmoke2", default_context_policy="exploration")
    row = svc.get_project(pid)
    assert row["name"] == "SvcSmoke2"
    assert row["status"] == "archived"
    assert row.get("lifecycle_status") == "active"
    assert row.get("default_context_policy") == "exploration"
    svc.update_project(pid, clear_default_context_policy=True)
    assert svc.get_project(pid).get("default_context_policy") is None
    svc.delete_project(pid)
    assert svc.get_project(pid) is None


@pytest.mark.smoke
def test_smoke_delete_confirmation_text_semantics():
    """Lösch-Dialog-Text deckt die dokumentierte Semantik ab (Regression)."""
    from app.gui.domains.operations.projects.projects_workspace import PROJECT_DELETE_INFORMATIVE_TEXT

    t = PROJECT_DELETE_INFORMATIVE_TEXT.lower()
    assert "chat" in t
    assert "global" in t
    assert "knowledge" in t or "rag" in t
    assert "datei" in t or "project_files" in t or "verknüpf" in t
    assert "aktiv" in t


@pytest.mark.smoke
def test_smoke_new_project_dialog_fields(qapplication):
    """Neues-Projekt-Dialog: optionale Phase-A-Felder lesbar."""
    dlg = NewProjectDialog()
    assert dlg.get_name() == ""
    assert dlg.get_lifecycle_status() == "active"
    assert dlg.get_planned_start_date() == ""
    dlg.close()


@pytest.mark.smoke
def test_smoke_projects_workspace_and_edit_dialog_instantiate(qapplication):
    """Workspace und Bearbeiten-Dialog sind importierbar und instanziierbar (ohne exec)."""
    from app.gui.domains.operations.projects.projects_workspace import ProjectsWorkspace
    from app.gui.domains.operations.projects.dialogs.project_edit_dialog import ProjectEditDialog

    ws = ProjectsWorkspace()
    assert ws.workspace_id == "operations_projects"

    dlg = ProjectEditDialog(
        {
            "project_id": 1,
            "name": "X",
            "description": "Y",
            "status": "active",
            "default_context_policy": None,
            "lifecycle_status": "active",
        },
        ws,
    )
    vals = dlg.get_values()
    name, desc, status, clear_pol, pol = vals[0], vals[1], vals[2], vals[3], vals[4]
    customer, ext_ref, int_code, lifecycle, pstart, pend = vals[5], vals[6], vals[7], vals[8], vals[9], vals[10]
    bamt, bcur, eff = vals[11], vals[12], vals[13]
    assert name == "X"
    assert clear_pol is True
    assert pol is None
    assert status == "active"
    assert customer is None
    assert lifecycle == "active"
    assert pstart == ""
    assert pend == ""
    assert bamt == ""
    assert bcur == ""
    assert eff == ""
    dlg.close()


@pytest.mark.smoke
def test_smoke_project_milestones_dialog_instantiate(qapplication):
    from app.gui.domains.operations.projects.dialogs.project_milestones_dialog import (
        ProjectMilestonesDialog,
    )

    dlg = ProjectMilestonesDialog({"project_id": 1, "name": "Demo"}, None)
    dlg.close()
