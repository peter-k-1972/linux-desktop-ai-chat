"""O4: Projekt-Quick-Action → Workflows mit Pending-Kontext und Run-Scope „Projekt“."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from app.core.db.database_manager import DatabaseManager
from app.gui.domains.operations.operations_context import (
    consume_pending_context,
    set_pending_context,
)
from app.gui.domains.operations.projects.panels.project_quick_actions_panel import (
    ProjectQuickActionsPanel,
)
from app.gui.domains.operations.projects.panels.project_overview_panel import (
    ProjectOverviewPanel,
)
from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.gui.domains.operations.workflows.workflow_workspace import WorkflowsWorkspace
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.persistence.workflow_repository import WorkflowRepository


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_operations_context_o4_keys_roundtrip():
    set_pending_context({"workflow_ops_scope": "project"})
    assert consume_pending_context() == {"workflow_ops_scope": "project"}
    assert consume_pending_context() == {}


def test_quick_actions_panel_workflows_signal():
    _app()
    panel = ProjectQuickActionsPanel()
    hits: list[int] = []
    panel.open_workflows_requested.connect(lambda: hits.append(1))
    panel.open_workflows_requested.emit()
    assert hits == [1]


def test_overview_quick_open_workflows_pending_and_show_area():
    _app()
    panel = ProjectOverviewPanel()
    panel.set_project({"project_id": 42, "name": "Testprojekt"})
    mock_host = MagicMock()
    with patch.object(panel, "_find_workspace_host", return_value=mock_host):
        with patch(
            "app.gui.domains.operations.operations_context.set_pending_context"
        ) as spc:
            with patch(
                "app.core.context.project_context_manager.get_project_context_manager"
            ) as gpcm:
                m = MagicMock()
                m.get_active_project_id.return_value = 42
                gpcm.return_value = m
                panel._on_quick_open_workflows()
    spc.assert_called_once_with({"workflow_ops_scope": "project"})
    mock_host.show_area.assert_called_once()
    args = mock_host.show_area.call_args[0]
    assert args[1] == "operations_workflows"


@pytest.fixture
def workflow_workspace_o4(tmp_path, monkeypatch):
    db_path = str(tmp_path / "o4.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    svc = WorkflowService(WorkflowRepository(db_path))
    monkeypatch.setattr(
        "app.gui.domains.operations.workflows.workflow_workspace.get_workflow_service",
        lambda: svc,
    )
    ws = WorkflowsWorkspace()
    return ws


def test_workflows_open_with_context_empty_noop(workflow_workspace_o4):
    ws = workflow_workspace_o4
    ws._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_WORKFLOW)
    ws.open_with_context({})
    assert ws._run_panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_WORKFLOW


def test_workflows_open_with_context_unknown_key_noop(workflow_workspace_o4):
    ws = workflow_workspace_o4
    ws._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_WORKFLOW)
    ws.open_with_context({"chat_id": 1})
    assert ws._run_panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_WORKFLOW


def test_workflows_open_with_context_project_sets_scope_and_refreshes(
    workflow_workspace_o4, monkeypatch
):
    ws = workflow_workspace_o4
    ws._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_WORKFLOW)
    calls: list[int] = []

    def _track_refresh():
        calls.append(1)

    monkeypatch.setattr(ws, "_refresh_runs", _track_refresh)
    ws.open_with_context({"workflow_ops_scope": "project"})
    assert ws._run_panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_PROJECT
    assert calls == [1]
