"""Smoke: WorkflowRunPanel O1 — Modi, Summaries, Detail."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_workflow_run_panel_instantiate_and_scope_switch():
    _app()
    panel = WorkflowRunPanel()
    assert panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_WORKFLOW
    panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_PROJECT)
    assert panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_PROJECT
    panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_ALL)
    assert panel.run_list_scope() == WorkflowRunPanel.RUN_SCOPE_ALL


def test_workflow_run_panel_summaries_then_full_detail():
    _app()
    panel = WorkflowRunPanel()
    panel.set_jump_context_workflow_id("w1")
    sums = [
        WorkflowRunSummary(
            run_id="r1",
            workflow_id="w1",
            workflow_name="N",
            workflow_version=1,
            project_id=1,
            status="completed",
            created_at=None,
            started_at=None,
            finished_at=None,
            error_message=None,
        )
    ]
    panel.set_run_summaries(
        sums,
        scope_caption="Test",
        empty_hint="",
    )
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        node_runs=[],
    )
    panel.set_full_run_detail(run)
    assert panel.current_run() is run
    panel.clear_full_run_detail()
    assert panel.current_run() is None


def test_panel_diagnosis_block_after_full_detail():
    _app()
    panel = WorkflowRunPanel()
    panel.set_jump_context_workflow_id("w1")
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        node_runs=[],
    )
    panel.set_full_run_detail(run)
    assert "Erfolgreich" in panel._diag_headline.text()
    run_fail = WorkflowRun(
        run_id="r2",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        node_runs=[
            NodeRun(
                node_run_id="n1",
                run_id="r2",
                node_id="n_x",
                node_type="tool_call",
                status=NodeRunStatus.FAILED,
                error_message="tool down",
            )
        ],
    )
    panel.set_full_run_detail(run_fail)
    assert "n_x" in panel._diag_headline.text() or "Fehlgeschlagen" in panel._diag_headline.text()


def test_jump_disabled_when_run_workflow_differs_from_editor():
    _app()
    panel = WorkflowRunPanel()
    panel.set_jump_context_workflow_id("editor_wf")
    sums = [
        WorkflowRunSummary(
            run_id="r1",
            workflow_id="other_wf",
            workflow_name="O",
            workflow_version=1,
            project_id=None,
            status="failed",
            created_at=None,
            started_at=None,
            finished_at=None,
            error_message="x",
        )
    ]
    panel.set_run_summaries(sums, scope_caption="", empty_hint="")
    run = WorkflowRun(
        run_id="r1",
        workflow_id="other_wf",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        node_runs=[
            NodeRun(
                node_run_id="n1",
                run_id="r1",
                node_id="n",
                node_type="noop",
                status=NodeRunStatus.COMPLETED,
            )
        ],
    )
    panel.set_full_run_detail(run)
    panel._node_table.selectRow(0)
    # Jump nur bei Übereinstimmung mit Editor-Workflow
    assert not panel._jump_allowed_for_current_run()
