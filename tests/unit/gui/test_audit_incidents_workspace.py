"""R1: Audit/Incidents-Workspace und Workflow-Sprung per Kontext."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.core.db.database_manager import DatabaseManager
from app.gui.domains.operations.audit_incidents.audit_incidents_workspace import AuditIncidentsWorkspace
from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.gui.domains.operations.workflows.workflow_workspace import WorkflowsWorkspace
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.persistence.workflow_repository import WorkflowRepository


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_audit_incidents_workspace_importable():
    assert AuditIncidentsWorkspace is not None


def test_audit_incidents_workspace_builds():
    _app()
    w = AuditIncidentsWorkspace()
    assert w.workspace_id == "audit_incidents"
    assert w._tabs.count() == 3


def test_audit_incidents_platform_tab_refresh_no_crash():
    _app()
    w = AuditIncidentsWorkspace()
    w._tabs.setCurrentIndex(2)
    w._platform.refresh()


def test_audit_incidents_open_with_context_platform_tab():
    _app()
    w = AuditIncidentsWorkspace()
    w.open_with_context({"audit_incidents_tab": "platform"})
    assert w._tabs.currentIndex() == 2


@pytest.fixture
def workflow_workspace_run_ctx(tmp_path, monkeypatch):
    db_path = str(tmp_path / "rctx.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    svc = WorkflowService(WorkflowRepository(db_path))
    monkeypatch.setattr(
        "app.gui.domains.operations.workflows.workflow_workspace.get_workflow_service",
        lambda: svc,
    )
    ws = WorkflowsWorkspace()
    return ws


def test_open_with_context_run_id_selects_when_all_scope(workflow_workspace_run_ctx, monkeypatch):
    ws = workflow_workspace_run_ctx
    ws._dirty = True
    sel: list[str] = []
    monkeypatch.setattr(ws._run_panel, "select_run_by_id", lambda rid: sel.append(rid))
    refreshes = []

    def _r():
        refreshes.append(1)

    monkeypatch.setattr(ws, "_refresh_runs", _r)
    ws.open_with_context({"workflow_ops_run_id": "wr_abc", "workflow_ops_workflow_id": "w1"})
    assert ws._run_panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_ALL
    assert refreshes == [1]
    assert sel == ["wr_abc"]


def test_open_with_context_run_id_loads_workflow_when_clean(workflow_workspace_run_ctx, monkeypatch):
    ws = workflow_workspace_run_ctx
    ws._dirty = False
    loads: list[str] = []
    monkeypatch.setattr(ws, "_load_workflow_id", lambda wid: loads.append(wid))
    monkeypatch.setattr(ws._run_panel, "select_run_by_id", lambda rid: loads.append(rid))
    ws.open_with_context({"workflow_ops_run_id": "wr_x", "workflow_ops_workflow_id": "w9"})
    assert loads == ["w9", "wr_x"]


def test_open_with_context_select_workflow_id_loads_when_clean(workflow_workspace_run_ctx, monkeypatch):
    ws = workflow_workspace_run_ctx
    ws._dirty = False
    loads: list[str] = []

    def _rl():
        loads.append("refresh_list")

    monkeypatch.setattr(ws, "_refresh_list", _rl)
    monkeypatch.setattr(ws, "_load_workflow_id", lambda wid: loads.append(wid))
    ws.open_with_context({"workflow_ops_select_workflow_id": "wf_demo"})
    assert loads == ["refresh_list", "wf_demo"]


def test_open_with_context_select_workflow_id_skips_when_dirty(workflow_workspace_run_ctx, monkeypatch):
    ws = workflow_workspace_run_ctx
    ws._dirty = True
    loads: list[str] = []
    monkeypatch.setattr(ws, "_refresh_list", lambda: loads.append("bad"))
    monkeypatch.setattr(ws, "_load_workflow_id", lambda wid: loads.append(wid))
    ws.open_with_context({"workflow_ops_select_workflow_id": "wf_demo"})
    assert loads == []
