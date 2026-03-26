"""Workflow QML bridge: Run-Scopes, Pending-Context, Presenter-Anbindung (kein WorkflowService im VM)."""

from __future__ import annotations

import copy

import pytest

from app.services.workflow_service import RunNotFoundError, WorkflowNotFoundError
from app.ui_application.presenters.workflow_studio_presenter import (
    RUN_SCOPE_ALL,
    RUN_SCOPE_PROJECT,
    RUN_SCOPE_WORKFLOW,
    WorkflowStudioPresenter,
)
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.status import NodeRunStatus, WorkflowDefinitionStatus, WorkflowRunStatus
from app.workflows.validation.graph_validator import ValidationResult
from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel


def _sample_definition() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_id="w1",
        name="W One",
        version=1,
        status=WorkflowDefinitionStatus.VALID,
        nodes=[
            WorkflowNode("start", "start", title="Start"),
            WorkflowNode("end", "end", title="End"),
        ],
        edges=[WorkflowEdge("e1", "start", "end")],
        project_id=7,
    )


def _failed_run() -> WorkflowRun:
    r = WorkflowRun(
        run_id="wr_1",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message="run-level",
        initial_input={"seed": 1},
    )
    r.node_runs = [
        NodeRun(
            node_run_id="nr1",
            run_id="wr_1",
            node_id="bad",
            node_type="noop",
            status=NodeRunStatus.FAILED,
            error_message="node-level",
        )
    ]
    return r


class _FakeWorkflowPort:
    def __init__(self) -> None:
        self.active_pid = 7
        self.definition = _sample_definition()
        self.w2 = copy.deepcopy(_sample_definition())
        self.w2.workflow_id = "w2"
        self.w2.name = "W Two"
        self.runs: dict[str, WorkflowRun] = {"wr_1": copy.deepcopy(_failed_run())}
        self.rerun_calls: list[tuple[str, dict | None]] = []
        self.from_previous_calls: list[tuple[str, dict | None]] = []
        self.start_run_calls: list[tuple[str, dict]] = []

    def get_active_project_id(self) -> int | None:
        return self.active_pid

    def list_workflows(self, *, project_scope_id, include_global: bool):
        if project_scope_id is not None and self.definition.project_id != project_scope_id:
            return []
        return [self.definition, self.w2]

    def list_run_summaries(self, *, workflow_id=None, project_id=None, status=None, limit=None):
        cap = limit if limit is not None else 50
        rows: list[WorkflowRunSummary] = []
        for run in sorted(self.runs.values(), key=lambda r: r.run_id, reverse=True):
            if workflow_id and run.workflow_id != workflow_id:
                continue
            wf_name = "W One" if run.workflow_id == "w1" else "W Two"
            pid = 7
            if project_id is not None and pid != project_id:
                continue
            st = run.status.value
            if status and st != status:
                continue
            rows.append(
                WorkflowRunSummary(
                    run_id=run.run_id,
                    workflow_id=run.workflow_id,
                    workflow_name=wf_name,
                    workflow_version=run.workflow_version,
                    project_id=pid,
                    status=st,
                    created_at=run.created_at,
                    started_at=run.started_at,
                    finished_at=run.finished_at,
                    error_message=run.error_message,
                )
            )
        return rows[:cap]

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        if workflow_id == "w1":
            return WorkflowDefinition.from_dict(self.definition.to_dict())
        if workflow_id == "w2":
            return WorkflowDefinition.from_dict(self.w2.to_dict())
        raise WorkflowNotFoundError(workflow_id)

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        if definition.workflow_id == "w1":
            self.definition = definition
        elif definition.workflow_id == "w2":
            self.w2 = definition
        return ValidationResult(is_valid=True)

    def validate_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        return ValidationResult(is_valid=True)

    def start_run(self, workflow_id: str, params: dict) -> str:
        self.start_run_calls.append((workflow_id, dict(params)))
        new = WorkflowRun(
            run_id="wr_new",
            workflow_id=workflow_id,
            workflow_version=1,
            status=WorkflowRunStatus.COMPLETED,
        )
        self.runs[new.run_id] = new
        return new.run_id

    def get_run(self, run_id: str) -> WorkflowRun:
        if run_id not in self.runs:
            raise RunNotFoundError(run_id)
        return copy.deepcopy(self.runs[run_id])

    def start_run_from_previous(
        self,
        run_id: str,
        initial_input_override: dict | None = None,
    ) -> WorkflowRun:
        self.rerun_calls.append((run_id, initial_input_override))
        self.from_previous_calls.append(
            (run_id, None if initial_input_override is None else dict(initial_input_override))
        )
        prev = self.get_run(run_id)
        new = WorkflowRun(
            run_id="wr_2",
            workflow_id=prev.workflow_id,
            workflow_version=prev.workflow_version,
            status=WorkflowRunStatus.COMPLETED,
        )
        self.runs[new.run_id] = new
        return new


class _FakeScheduleReadPort:
    def __init__(self) -> None:
        self.calls = 0
        self.rows: list[dict] = [
            {
                "scheduleId": "sch_1",
                "workflowId": "w1",
                "workflowName": "W One",
                "enabled": True,
                "nextRunAt": "2099-01-01T00:00:00+00:00",
            }
        ]

    def list_schedule_summaries(self, *, project_scope_id, include_global: bool):
        self.calls += 1
        return list(self.rows)


def test_presenter_run_scope_workflow_requires_loaded_id() -> None:
    port = _FakeWorkflowPort()
    p = WorkflowStudioPresenter(port)
    sums, cap, empty = p.fetch_run_summaries(
        RUN_SCOPE_WORKFLOW, loaded_workflow_id=None, status_filter=None
    )
    assert sums == []
    assert "kein workflow geladen" in cap.lower()
    assert empty


def test_presenter_run_scope_project_requires_active_project() -> None:
    port = _FakeWorkflowPort()
    port.active_pid = None
    p = WorkflowStudioPresenter(port)
    sums, cap, _ = p.fetch_run_summaries(
        RUN_SCOPE_PROJECT, loaded_workflow_id="w1", status_filter=None
    )
    assert sums == []
    assert "kein projekt aktiv" in cap.lower()


def test_presenter_run_scope_all_returns_rows() -> None:
    port = _FakeWorkflowPort()
    p = WorkflowStudioPresenter(port)
    sums, _, _ = p.fetch_run_summaries(RUN_SCOPE_ALL, loaded_workflow_id=None, status_filter=None)
    assert len(sums) == 1
    rows = p.run_summary_rows(sums)
    assert rows[0]["workflowId"] == "w1"
    assert rows[0]["errorPreview"]


def test_viewmodel_init_and_refresh_runs_stable(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.setRunListScope(RUN_SCOPE_ALL)
        vm.refreshRuns()
        assert vm.runs.rowCount() == 1
    finally:
        vm.dispose()


def test_viewmodel_scope_switch_deterministic(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.setRunListScope(RUN_SCOPE_WORKFLOW)
        vm.refreshRuns()
        assert vm.runs.rowCount() == 1
        vm.setRunListScope(RUN_SCOPE_PROJECT)
        vm.refreshRuns()
        assert vm.runs.rowCount() == 1
        port.active_pid = 99
        vm.refreshRuns()
        assert vm.runs.rowCount() == 0
    finally:
        vm.dispose()


def test_viewmodel_pending_context_run_id_respects_dirty(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        assert vm.graphDirty is True
        ctx = '{"workflow_ops_run_id":"wr_1","workflow_ops_workflow_id":"w1"}'
        vm.applyShellPendingContextJson(ctx)
        assert vm.runListScope == RUN_SCOPE_ALL
        assert vm.selectedRunId == "wr_1"
    finally:
        vm.dispose()


def test_viewmodel_pending_project_scope_sets_run_list_and_list_filter(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.applyShellPendingContextJson('{"workflow_ops_scope":"project"}')
        assert vm.runListScope == RUN_SCOPE_PROJECT
        assert vm._list_project_scope_id == 7
    finally:
        vm.dispose()


def test_viewmodel_pending_context_preloads_workflow_when_clean(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        ctx = '{"workflow_ops_run_id":"wr_1","workflow_ops_workflow_id":"w1"}'
        vm.applyShellPendingContextJson(ctx)
        assert vm.selectedWorkflow == "w1"
        assert vm.selectedRunId == "wr_1"
    finally:
        vm.dispose()


def test_viewmodel_diagnostics_from_port(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        assert "fehlgeschlagen" in vm.runDiagnosticsHeadline.lower()
        assert vm.nodeRuns.rowCount() == 1
        vm.selectNodeRun("nr1")
        assert "node-level" in vm.selectedNodeRunErrorText
    finally:
        vm.dispose()


def test_viewmodel_rerun_wires_port(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        vm.rerunSelectedRunSameInputs()
        assert port.rerun_calls == [("wr_1", None)]
        assert port.from_previous_calls[-1] == ("wr_1", None)
        assert vm.selectedRunId == "wr_2"
    finally:
        vm.dispose()


def test_rerun_override_uses_parser_and_passes_dict(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        vm.setRerunOverrideInputJson('{"x": 2}')
        vm.startRerunWithCommittedOverride()
        assert port.from_previous_calls[-1] == ("wr_1", {"x": 2})
    finally:
        vm.dispose()


def test_rerun_override_whitespace_only_errors(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        vm.setRerunOverrideInputJson("  \n  ")
        vm.startRerunWithCommittedOverride()
        assert "json eingeben" in vm.lastError.lower() or "gleiche eingaben" in vm.lastError.lower()
        assert port.from_previous_calls == []
    finally:
        vm.dispose()


def test_rerun_override_invalid_json_errors(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        vm.setRerunOverrideInputJson("{")
        vm.startRerunWithCommittedOverride()
        assert vm.lastError
        assert port.from_previous_calls == []
    finally:
        vm.dispose()


def test_sync_rerun_override_from_run(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.selectRun("wr_1")
        vm.syncRerunOverrideFromSelectedRun()
        assert '"seed"' in vm.rerunOverrideInputJson
        assert "1" in vm.rerunOverrideInputJson
    finally:
        vm.dispose()


def test_refresh_schedules_uses_read_port(qapplication) -> None:
    port = _FakeWorkflowPort()
    sch = _FakeScheduleReadPort()
    vm = WorkflowStudioViewModel(port=port, schedule_read_port=sch)
    try:
        assert sch.calls >= 1
        vm.refreshSchedules()
        assert sch.calls >= 2
        assert vm.schedules.rowCount() == 1
    finally:
        vm.dispose()


def test_presenter_parse_initial_input_matches_dialog_semantics() -> None:
    d, err = WorkflowStudioPresenter.parse_initial_input_json("")
    assert err is None and d == {}
    d, err = WorkflowStudioPresenter.parse_initial_input_json("   ")
    assert err is None and d == {}
    d, err = WorkflowStudioPresenter.parse_initial_input_json('{"a": 1}')
    assert err is None and d == {"a": 1}
    d, err = WorkflowStudioPresenter.parse_initial_input_json("[1,2]")
    assert d is None and err == "Es muss ein JSON-Objekt sein."
    d, err = WorkflowStudioPresenter.parse_initial_input_json("{no")
    assert d is None and err is not None


def test_start_test_run_passes_parsed_input_to_port(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.setTestRunInputJson('{"msg": "hi"}')
        vm.startTestRun()
        assert port.start_run_calls == [("w1", {"msg": "hi"})]
        assert vm.selectedRunId == "wr_new"
    finally:
        vm.dispose()


def test_apply_shell_blocked_while_graph_action_pending(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        vm.requestSelectWorkflow("w2")
        assert vm.graphActionPending is True
        vm.applyShellPendingContextJson('{"workflow_ops_select_workflow_id":"w2"}')
        assert "blockiert" in vm.lastError.lower()
        assert vm.graphActionPending is True
    finally:
        vm.dispose()


def test_pending_context_defers_workflow_select_when_graph_dirty(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        vm.applyShellPendingContextJson('{"workflow_ops_select_workflow_id":"w2"}')
        assert vm.graphActionPending is True
        assert vm.graphActionKind == "apply_context"
        assert vm.selectedWorkflow == "w1"
        vm.resolveGraphActionDiscard()
        assert vm.graphActionPending is False
        assert vm.selectedWorkflow == "w2"
        assert vm.graphDirty is False
    finally:
        vm.dispose()


def test_pending_context_deferred_resolve_save_applies_select_and_emits_clear_once(qapplication) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    clears: list[int] = []
    vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        vm.applyShellPendingContextJson('{"workflow_ops_select_workflow_id":"w2"}')
        assert vm.graphActionPending is True
        vm.resolveGraphActionSave()
        assert vm.graphActionPending is False
        assert vm.selectedWorkflow == "w2"
        assert vm.graphDirty is False
        assert clears == [1]
    finally:
        vm.dispose()


def test_pending_context_deferred_resolve_save_invalid_keeps_pending_and_no_shell_clear(
    qapplication,
) -> None:
    class _Port(_FakeWorkflowPort):
        def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
            return ValidationResult(is_valid=False, errors=["simulated-save-invalid"])

    port = _Port()
    vm = WorkflowStudioViewModel(port=port)
    clears: list[int] = []
    vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        vm.applyShellPendingContextJson('{"workflow_ops_select_workflow_id":"w2"}')
        assert vm.graphActionPending is True
        vm.resolveGraphActionSave()
        assert vm.graphActionPending is True
        assert vm.selectedWorkflow == "w1"
        assert vm.graphDirty is True
        assert clears == []
        assert "validierung" in vm.lastError.lower()
    finally:
        vm.dispose()


def test_pending_context_deferred_resolve_cancel_keeps_workflow_and_shell_clear_not_emitted(
    qapplication,
) -> None:
    port = _FakeWorkflowPort()
    vm = WorkflowStudioViewModel(port=port)
    clears: list[int] = []
    vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    try:
        vm.requestSelectWorkflow("w1")
        vm.addNode("agent")
        vm.applyShellPendingContextJson('{"workflow_ops_select_workflow_id":"w2"}')
        assert vm.graphActionPending is True
        vm.resolveGraphActionCancel()
        assert vm.graphActionPending is False
        assert vm.selectedWorkflow == "w1"
        assert vm.graphDirty is True
        assert clears == []
        assert "abgebrochen" in vm.lastError.lower()
    finally:
        vm.dispose()


def test_workflow_viewmodel_has_no_get_workflow_service_import() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    src = (root / "python_bridge/workflows/workflow_viewmodel.py").read_text(encoding="utf-8")
    assert "get_workflow_service" not in src
