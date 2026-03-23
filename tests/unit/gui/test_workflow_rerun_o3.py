"""O3 Re-Run: Panel-Freigabe, Signal; Workspace ruft start_run_from_previous auf."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from app.core.db.database_manager import DatabaseManager
from app.gui.domains.operations.workflows.dialogs.workflow_input_dialog import WorkflowInputDialog
from app.gui.domains.operations.workflows.workflow_workspace import WorkflowsWorkspace
from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import WorkflowRun
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowRunStatus


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _minimal_valid_def(wid: str) -> WorkflowDefinition:
    return WorkflowDefinition(
        wid,
        "T",
        [
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        [WorkflowEdge("a1", "s", "e")],
    )


def test_workflow_input_dialog_prefills_json():
    _app()
    dlg = WorkflowInputDialog(None, initial_input={"a": 1})
    assert '"a"' in dlg._edit.toPlainText() and "1" in dlg._edit.toPlainText()


def test_rerun_button_disabled_without_full_run():
    _app()
    panel = WorkflowRunPanel()
    assert not panel._btn_rerun.isEnabled()


def test_rerun_enabled_after_full_detail_with_workflow_id():
    _app()
    panel = WorkflowRunPanel()
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        initial_input={"x": 1},
        node_runs=[],
    )
    panel.set_full_run_detail(run)
    assert panel._btn_rerun.isEnabled()
    panel.clear_full_run_detail()
    assert not panel._btn_rerun.isEnabled()


def test_rerun_disabled_when_workflow_id_blank():
    _app()
    panel = WorkflowRunPanel()
    run = WorkflowRun(
        run_id="r1",
        workflow_id="   ",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        node_runs=[],
    )
    panel.set_full_run_detail(run)
    assert not panel._btn_rerun.isEnabled()


def test_rerun_button_emits_signal_when_enabled():
    _app()
    panel = WorkflowRunPanel()
    panel.show()
    hits: list[bool] = []
    panel.rerun_requested.connect(lambda: hits.append(True))
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        node_runs=[],
    )
    panel.set_full_run_detail(run)
    QTest.mouseClick(panel._btn_rerun, Qt.MouseButton.LeftButton)
    assert hits == [True]


@pytest.fixture
def rerun_workspace_service(tmp_path):
    db_path = str(tmp_path / "rerun_ws.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    svc = WorkflowService(WorkflowRepository(db_path))
    d = _minimal_valid_def("ws_rerun_wf")
    svc.save_workflow(d)
    svc.start_run("ws_rerun_wf", {"seed": 1})
    return svc


def test_workspace_rerun_calls_start_run_from_previous(rerun_workspace_service):
    _app()
    svc = rerun_workspace_service
    hist = svc.list_runs(workflow_id="ws_rerun_wf")[0]

    dlg_instance = MagicMock()
    dlg_instance.exec.return_value = QDialog.DialogCode.Accepted
    dlg_instance.get_input.return_value = {"seed": 2}

    with patch(
        "app.gui.domains.operations.workflows.workflow_workspace.get_workflow_service",
        return_value=svc,
    ):
        with patch(
            "app.gui.domains.operations.workflows.workflow_workspace.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            with patch(
                "app.gui.domains.operations.workflows.workflow_workspace.QMessageBox.information",
            ):
                with patch(
                    "app.gui.domains.operations.workflows.workflow_workspace.WorkflowInputDialog",
                    return_value=dlg_instance,
                ):
                    ws = WorkflowsWorkspace()
                    ws._run_panel.set_full_run_detail(svc.get_run(hist.run_id))
                    ws._on_rerun()

    runs_after = svc.list_runs(workflow_id="ws_rerun_wf")
    assert len(runs_after) == 2
    assert svc.get_run(hist.run_id).initial_input == {"seed": 1}
    inputs = {r.run_id: r.initial_input for r in runs_after}
    assert inputs[hist.run_id] == {"seed": 1}
    other_id = next(rid for rid in inputs if rid != hist.run_id)
    assert inputs[other_id] == {"seed": 2}
