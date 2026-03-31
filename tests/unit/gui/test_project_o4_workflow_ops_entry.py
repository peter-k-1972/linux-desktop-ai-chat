"""O4: Projekt-Quick-Action → Workflows mit Pending-Kontext und Run-Scope „Projekt“."""

from __future__ import annotations

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
    class _ReadPort:
        def load_project_overview(self, project_id: int):
            del project_id
            return None

        def subscribe_active_project_changed(self, listener):
            del listener
            return type("_H", (), {"dispose": lambda self: None})()

    class _CommandPort:
        def select_project(self, project_id: int | None) -> None:
            del project_id

        def set_active_project(self, project_id: int | None):
            del project_id
            return type("_R", (), {"ok": True, "message": None})()

    class _HostCallbacks:
        def __init__(self) -> None:
            self.workflow_calls: list[int] = []

        def on_project_selection_changed(self, payload) -> None:
            del payload

        def on_request_open_chat(self, project_id: int, chat_id: int | None = None) -> None:
            del project_id, chat_id

        def on_request_open_prompt_studio(self, project_id: int, prompt_id: int | None = None) -> None:
            del project_id, prompt_id

        def on_request_open_knowledge(self, project_id: int, source_path: str | None = None) -> None:
            del project_id, source_path

        def on_request_open_workflows(self, project_id: int) -> None:
            self.workflow_calls.append(project_id)

        def on_request_open_agent_tasks(self, project_id: int) -> None:
            del project_id

        def on_request_set_active_project(self, project_id: int | None) -> None:
            del project_id

    host = _HostCallbacks()
    panel = ProjectOverviewPanel(
        read_port=_ReadPort(),
        command_port=_CommandPort(),
        host_callbacks=host,
    )
    panel.set_project({"project_id": 42, "name": "Testprojekt"})
    panel._on_quick_open_workflows()
    assert host.workflow_calls == [42]


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
