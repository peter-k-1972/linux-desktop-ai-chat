from __future__ import annotations

import sqlite3
from unittest.mock import patch

from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.gui.domains.operations.workflows.workflow_workspace import WorkflowsWorkspace


class _MissingSchemaWorkflowService:
    def list_workflows(self, *, project_scope_id, include_global: bool):
        raise sqlite3.OperationalError("no such table: workflows")

    def list_run_summaries(self, *, workflow_id=None, project_id=None, status=None, limit=None):
        raise sqlite3.OperationalError("no such table: workflow_runs")


def test_refresh_list_missing_schema_does_not_open_modal(qapplication):
    with patch(
        "app.gui.domains.operations.workflows.workflow_workspace.get_workflow_service",
        return_value=_MissingSchemaWorkflowService(),
    ):
        with patch(
            "app.gui.domains.operations.workflows.workflow_workspace.QTimer.singleShot"
        ):
            ws = WorkflowsWorkspace()

    with patch(
        "app.gui.domains.operations.workflows.workflow_workspace.QMessageBox.critical"
    ) as critical:
        ws._refresh_list()

    assert critical.call_count == 0
    assert ws._list_panel._table.rowCount() == 0


def test_refresh_runs_missing_schema_does_not_open_modal(qapplication):
    with patch(
        "app.gui.domains.operations.workflows.workflow_workspace.get_workflow_service",
        return_value=_MissingSchemaWorkflowService(),
    ):
        with patch(
            "app.gui.domains.operations.workflows.workflow_workspace.QTimer.singleShot"
        ):
            ws = WorkflowsWorkspace()

    ws._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_ALL, silent=True)
    with patch(
        "app.gui.domains.operations.workflows.workflow_workspace.QMessageBox.warning"
    ) as warning:
        ws._refresh_runs()

    assert warning.call_count == 0
    assert ws._run_panel._runs_table.rowCount() == 0
