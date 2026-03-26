"""
QML-Kontextobjekt ``workflowStudio``: Workflows, Graph, Inspector, Run-Historie.

Bridge → Presenter (:class:`WorkflowStudioPresenter`) → Port → Adapter → Service.

Zentrale Slots: reload, refreshRuns, requestSelectWorkflow, setRunListScope, setRunStatusFilter,
selectRun, selectNodeRun, rerunSelectedRunSameInputs, startRerunWithCommittedOverride,
setRerunOverrideInputJson, syncRerunOverrideFromSelectedRun, startTestRun, setTestRunInputJson,
refreshSchedules,
resolveGraphActionSave/Discard/Cancel, … (Graph wie zuvor).
"""

from __future__ import annotations

import copy
import json
import logging
import uuid

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.gui.events.project_events import subscribe_project_events, unsubscribe_project_events
from app.services.workflow_service import (
    IncompleteHistoricalRunError,
    RunNotFoundError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.ui_application.adapters.service_qml_workflow_canvas_adapter import ServiceQmlWorkflowCanvasAdapter
from app.ui_application.adapters.service_qml_workflow_schedule_read_adapter import (
    ServiceQmlWorkflowScheduleReadAdapter,
)
from app.ui_application.presenters.workflow_studio_presenter import (
    RUN_SCOPE_ALL,
    RUN_SCOPE_PROJECT,
    RUN_SCOPE_WORKFLOW,
    WorkflowStudioPresenter,
)
from app.ui_application.ports.qml_workflow_canvas_port import QmlWorkflowCanvasPort
from app.ui_application.ports.qml_workflow_schedule_read_port import QmlWorkflowScheduleReadPort
from app.workflows.models.definition import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowNode,
    effective_edge_flow_kind,
)
from app.workflows.models.run import WorkflowRun

from python_bridge.workflows.workflow_models import (
    ScheduleSummaryListModel,
    WorkflowGraphEdgeModel,
    WorkflowGraphNodeModel,
    WorkflowNodeRunListModel,
    WorkflowRunHistoryModel,
    WorkflowSummaryListModel,
)

logger = logging.getLogger(__name__)

NODE_W = 168.0
NODE_H = 80.0

_TYPE_TO_ROLE: dict[str, str] = {
    "agent": "agent",
    "prompt_build": "prompt",
    "tool_call": "tool",
    "chain_delegate": "model",
    "context_load": "memory",
    "noop": "condition",
    "start": "start",
    "end": "end",
}

_ROLE_TO_TYPE: dict[str, str] = {
    "agent": "agent",
    "prompt": "prompt_build",
    "tool": "tool_call",
    "model": "chain_delegate",
    "memory": "context_load",
    "condition": "noop",
}


def _node_role_key(node_type: str) -> str:
    return _TYPE_TO_ROLE.get((node_type or "").strip().lower(), "agent")


class WorkflowStudioViewModel(QObject):
    workflowsChanged = Signal()
    selectedWorkflowChanged = Signal()
    nodesChanged = Signal()
    edgesChanged = Signal()
    runsChanged = Signal()
    selectedNodeChanged = Signal()
    lastErrorChanged = Signal()
    runBusyChanged = Signal()
    pendingEdgeSourceChanged = Signal()
    runScopeCaptionChanged = Signal()
    runEmptyHintChanged = Signal()
    runListScopeChanged = Signal()
    runStatusFilterChanged = Signal()
    selectedRunIdChanged = Signal()
    runDiagnosticsChanged = Signal()
    nodeRunsChanged = Signal()
    selectedNodeRunDetailChanged = Signal()
    graphDirtyChanged = Signal()
    graphActionPendingChanged = Signal()
    graphActionKindChanged = Signal()
    graphActionTargetWorkflowIdChanged = Signal()
    graphActionPromptChanged = Signal()
    testRunInputJsonChanged = Signal()
    rerunOverrideInputJsonChanged = Signal()
    shellPendingContextClearSuggested = Signal()

    def __init__(
        self,
        port: QmlWorkflowCanvasPort | None = None,
        schedule_read_port: QmlWorkflowScheduleReadPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlWorkflowCanvasPort = port or ServiceQmlWorkflowCanvasAdapter()
        self._schedule_read_port: QmlWorkflowScheduleReadPort = (
            schedule_read_port if schedule_read_port is not None else ServiceQmlWorkflowScheduleReadAdapter()
        )
        self._presenter = WorkflowStudioPresenter(self._port)
        self._workflows = WorkflowSummaryListModel(self)
        self._nodes = WorkflowGraphNodeModel(self)
        self._edges = WorkflowGraphEdgeModel(self)
        self._runs = WorkflowRunHistoryModel(self)
        self._node_runs = WorkflowNodeRunListModel(self)
        self._definition: WorkflowDefinition | None = None
        self._workflow_id: str | None = None
        self._selected_node_id: str | None = None
        self._last_error = ""
        self._run_busy = False
        self._pending_edge_source: str | None = None
        self._list_project_scope_id: int | None = None
        self._run_list_scope: str = RUN_SCOPE_WORKFLOW
        self._run_status_filter: str | None = None
        self._run_scope_caption = ""
        self._run_empty_hint = ""
        self._graph_dirty = False
        self._selected_run_id: str | None = None
        self._current_run: WorkflowRun | None = None
        self._selected_node_run_id: str | None = None
        self._diag_headline = "—"
        self._diag_summary = "—"
        self._diag_detail = "—"
        self._run_error_full = ""
        self._failed_node_id = ""
        self._failed_node_type = ""
        self._failed_node_error_full = ""
        self._node_run_input_json = ""
        self._node_run_output_json = ""
        self._node_run_error_text = ""
        self._test_run_input_json = "{}"
        self._graph_action_pending = False
        self._graph_action_kind = ""
        self._graph_action_target_workflow_id = ""
        self._deferred_context: dict[str, object] | None = None
        self._graph_action_prompt = ""
        self._schedules = ScheduleSummaryListModel(self)
        self._rerun_override_input_json = ""

        self._project_event_handler = self._on_project_context_changed
        subscribe_project_events(self._project_event_handler)

        self.reload()

    def dispose(self) -> None:
        unsubscribe_project_events(self._project_event_handler)

    def _on_project_context_changed(self, _payload: dict) -> None:
        self.reload()

    # --- models ---
    def _get_workflows(self) -> WorkflowSummaryListModel:
        return self._workflows

    workflows = Property(QObject, _get_workflows, notify=workflowsChanged)

    def _get_nodes(self) -> WorkflowGraphNodeModel:
        return self._nodes

    nodes = Property(QObject, _get_nodes, notify=nodesChanged)

    def _get_edges(self) -> WorkflowGraphEdgeModel:
        return self._edges

    edges = Property(QObject, _get_edges, notify=edgesChanged)

    def _get_runs(self) -> WorkflowRunHistoryModel:
        return self._runs

    runs = Property(QObject, _get_runs, notify=runsChanged)

    def _get_node_runs(self) -> WorkflowNodeRunListModel:
        return self._node_runs

    nodeRuns = Property(QObject, _get_node_runs, constant=True)

    def _get_sel_wf(self) -> str:
        return self._workflow_id or ""

    selectedWorkflow = Property(str, _get_sel_wf, notify=selectedWorkflowChanged)

    def _get_sel_node(self) -> str:
        return self._selected_node_id or ""

    selectedNodeId = Property(str, _get_sel_node, notify=selectedNodeChanged)

    def _get_last_err(self) -> str:
        return self._last_error

    lastError = Property(str, _get_last_err, notify=lastErrorChanged)

    def _get_busy(self) -> bool:
        return self._run_busy

    runBusy = Property(bool, _get_busy, notify=runBusyChanged)

    def _get_pending_edge(self) -> str:
        return self._pending_edge_source or ""

    pendingEdgeSource = Property(str, _get_pending_edge, notify=pendingEdgeSourceChanged)

    def _get_title(self) -> str:
        if not self._definition:
            return ""
        return self._definition.name

    selectedWorkflowTitle = Property(str, _get_title, notify=selectedWorkflowChanged)

    def _get_node_title(self) -> str:
        n = self._current_node()
        return (n.title if n else "") or ""

    selectedNodeTitle = Property(str, _get_node_title, notify=selectedNodeChanged)

    def _get_node_role(self) -> str:
        n = self._current_node()
        return _node_role_key(n.node_type) if n else ""

    selectedNodeRoleKey = Property(str, _get_node_role, notify=selectedNodeChanged)

    def _get_node_type(self) -> str:
        n = self._current_node()
        return (n.node_type if n else "") or ""

    selectedNodeType = Property(str, _get_node_type, notify=selectedNodeChanged)

    def _get_node_desc(self) -> str:
        n = self._current_node()
        return (n.description if n else "") or ""

    selectedNodeDescription = Property(str, _get_node_desc, notify=selectedNodeChanged)

    def _get_run_scope_cap(self) -> str:
        return self._run_scope_caption

    runScopeCaption = Property(str, _get_run_scope_cap, notify=runScopeCaptionChanged)

    def _get_run_empty(self) -> str:
        return self._run_empty_hint

    runEmptyHint = Property(str, _get_run_empty, notify=runEmptyHintChanged)

    def _get_run_list_scope(self) -> str:
        return self._run_list_scope

    runListScope = Property(str, _get_run_list_scope, notify=runListScopeChanged)

    def _get_run_status_filter(self) -> str:
        return self._run_status_filter or ""

    runStatusFilter = Property(str, _get_run_status_filter, notify=runStatusFilterChanged)

    def _get_sel_run(self) -> str:
        return self._selected_run_id or ""

    selectedRunId = Property(str, _get_sel_run, notify=selectedRunIdChanged)

    def _get_dh(self) -> str:
        return self._diag_headline

    runDiagnosticsHeadline = Property(str, _get_dh, notify=runDiagnosticsChanged)

    def _get_ds(self) -> str:
        return self._diag_summary

    runDiagnosticsSummary = Property(str, _get_ds, notify=runDiagnosticsChanged)

    def _get_dd(self) -> str:
        return self._diag_detail

    runDiagnosticsDetail = Property(str, _get_dd, notify=runDiagnosticsChanged)

    def _get_ref(self) -> str:
        return self._run_error_full

    runErrorFull = Property(str, _get_ref, notify=runDiagnosticsChanged)

    def _get_fni(self) -> str:
        return self._failed_node_id

    failedNodeId = Property(str, _get_fni, notify=runDiagnosticsChanged)

    def _get_fnt(self) -> str:
        return self._failed_node_type

    failedNodeType = Property(str, _get_fnt, notify=runDiagnosticsChanged)

    def _get_fne(self) -> str:
        return self._failed_node_error_full

    failedNodeErrorFull = Property(str, _get_fne, notify=runDiagnosticsChanged)

    def _get_ini(self) -> str:
        if not self._current_run:
            return ""
        return self._presenter.json_preview(dict(self._current_run.initial_input or {}))

    runInitialInputJson = Property(str, _get_ini, notify=runDiagnosticsChanged)

    def _get_nrij(self) -> str:
        return self._node_run_input_json

    selectedNodeRunInputJson = Property(str, _get_nrij, notify=selectedNodeRunDetailChanged)

    def _get_nroj(self) -> str:
        return self._node_run_output_json

    selectedNodeRunOutputJson = Property(str, _get_nroj, notify=selectedNodeRunDetailChanged)

    def _get_nret(self) -> str:
        return self._node_run_error_text

    selectedNodeRunErrorText = Property(str, _get_nret, notify=selectedNodeRunDetailChanged)

    def _get_gd(self) -> bool:
        return self._graph_dirty

    graphDirty = Property(bool, _get_gd, notify=graphDirtyChanged)

    def _get_tri(self) -> str:
        return self._test_run_input_json

    testRunInputJson = Property(str, _get_tri, notify=testRunInputJsonChanged)

    def _get_rerun_ov(self) -> str:
        return self._rerun_override_input_json

    rerunOverrideInputJson = Property(str, _get_rerun_ov, notify=rerunOverrideInputJsonChanged)

    def _get_schedules(self) -> ScheduleSummaryListModel:
        return self._schedules

    schedules = Property(QObject, _get_schedules, constant=True)

    def _get_gap(self) -> bool:
        return self._graph_action_pending

    graphActionPending = Property(bool, _get_gap, notify=graphActionPendingChanged)

    def _get_gak(self) -> str:
        return self._graph_action_kind

    graphActionKind = Property(str, _get_gak, notify=graphActionKindChanged)

    def _get_gat(self) -> str:
        return self._graph_action_target_workflow_id

    graphActionTargetWorkflowId = Property(str, _get_gat, notify=graphActionTargetWorkflowIdChanged)

    def _get_gapr(self) -> str:
        return self._graph_action_prompt

    graphActionPrompt = Property(str, _get_gapr, notify=graphActionPromptChanged)

    def _current_node(self) -> WorkflowNode | None:
        if not self._definition or not self._selected_node_id:
            return None
        return self._definition.node_by_id(self._selected_node_id)

    def _set_error(self, msg: str) -> None:
        if self._last_error != msg:
            self._last_error = msg
            self.lastErrorChanged.emit()

    def _set_busy(self, v: bool) -> None:
        if self._run_busy != v:
            self._run_busy = v
            self.runBusyChanged.emit()

    def _mark_graph_dirty(self) -> None:
        if not self._graph_dirty:
            self._graph_dirty = True
            self.graphDirtyChanged.emit()

    def _clear_graph_dirty(self) -> None:
        if self._graph_dirty:
            self._graph_dirty = False
            self.graphDirtyChanged.emit()

    def _notify_graph_action_props(self) -> None:
        self.graphActionPendingChanged.emit()
        self.graphActionKindChanged.emit()
        self.graphActionTargetWorkflowIdChanged.emit()
        self.graphActionPromptChanged.emit()

    def _clear_graph_action(self) -> None:
        self._graph_action_pending = False
        self._graph_action_kind = ""
        self._graph_action_target_workflow_id = ""
        self._deferred_context = None
        self._graph_action_prompt = ""
        self._notify_graph_action_props()

    def _begin_graph_action(
        self,
        *,
        kind: str,
        target_workflow_id: str,
        deferred_context: dict[str, object] | None,
        prompt: str,
    ) -> None:
        self._graph_action_pending = True
        self._graph_action_kind = kind
        self._graph_action_target_workflow_id = target_workflow_id
        self._deferred_context = deferred_context
        self._graph_action_prompt = prompt
        self._notify_graph_action_props()

    def _reload_current_workflow_from_disk(self) -> bool:
        if not self._workflow_id:
            return True
        try:
            raw = self._port.load_workflow(self._workflow_id)
        except Exception as e:
            self._set_error(str(e))
            return False
        self._definition = WorkflowDefinition.from_dict(copy.deepcopy(raw.to_dict()))
        self._push_graph_models()
        self.nodesChanged.emit()
        self.edgesChanged.emit()
        self.selectedNodeChanged.emit()
        self._clear_graph_dirty()
        return True

    def _clear_run_detail(self) -> None:
        self._selected_run_id = None
        self._current_run = None
        self._runs.set_selected_run(None)
        self._diag_headline = "—"
        self._diag_summary = "—"
        self._diag_detail = "—"
        self._run_error_full = ""
        self._failed_node_id = ""
        self._failed_node_type = ""
        self._failed_node_error_full = ""
        self._node_runs.set_rows([])
        self._selected_node_run_id = None
        self._node_run_input_json = ""
        self._node_run_output_json = ""
        self._node_run_error_text = ""
        self.selectedRunIdChanged.emit()
        self.runDiagnosticsChanged.emit()
        self.nodeRunsChanged.emit()
        self.selectedNodeRunDetailChanged.emit()

    def _apply_run_detail(self, run: WorkflowRun) -> None:
        self._current_run = run
        d = self._presenter.diagnostics_for_run(run)
        self._diag_headline = d["headline"]
        self._diag_summary = d["summary"]
        self._diag_detail = d["detail"]
        self._run_error_full = d["runErrorFull"]
        self._failed_node_id = d["failedNodeId"]
        self._failed_node_type = d["failedNodeType"]
        self._failed_node_error_full = d["failedNodeErrorFull"]
        rows = self._presenter.node_run_rows(run)
        self._node_runs.set_rows(rows, self._selected_node_run_id)
        self._node_run_input_json = ""
        self._node_run_output_json = ""
        self._node_run_error_text = ""
        self.runDiagnosticsChanged.emit()
        self.nodeRunsChanged.emit()
        self.selectedNodeRunDetailChanged.emit()

    def _refresh_runs(self) -> None:
        try:
            sums, caption, empty = self._presenter.fetch_run_summaries(
                self._run_list_scope,
                loaded_workflow_id=self._workflow_id,
                status_filter=self._run_status_filter,
            )
        except Exception:
            logger.exception("run summaries")
            sums, caption, empty = [], "Runs", "Fehler beim Laden der Run-Liste."
        rows_obj = self._presenter.run_summary_rows(sums)
        rows: list[dict[str, object]] = [dict(r) for r in rows_obj]
        self._run_scope_caption = caption
        self._run_empty_hint = empty
        self._runs.set_rows(rows, self._selected_run_id)
        self.runsChanged.emit()
        self.runScopeCaptionChanged.emit()
        self.runEmptyHintChanged.emit()
        if self._selected_run_id:
            ids = {str(r["runId"]) for r in rows}
            if self._selected_run_id not in ids:
                self._clear_run_detail()
            else:
                try:
                    run = self._port.get_run(self._selected_run_id)
                    self._apply_run_detail(run)
                except Exception:
                    logger.exception("refresh run detail")
                    self._clear_run_detail()

    @Slot()
    def refreshRuns(self) -> None:
        """Nur Run-Liste (wie Run-Panel „Runs aktualisieren“ in der Haupt-GUI)."""
        self._refresh_runs()

    @Slot()
    def reload(self) -> None:
        self._set_error("")
        try:
            items = self._port.list_workflows(
                project_scope_id=self._list_project_scope_id,
                include_global=True,
            )
        except Exception:
            logger.exception("workflow list")
            items = []
        rows: list[dict[str, object]] = []
        for w in items:
            wid = w.workflow_id
            rows.append(
                {
                    "workflowId": wid,
                    "name": w.name or wid,
                    "version": w.version,
                    "subline": f"v{w.version} · {w.status.value}",
                }
            )
        self._workflows.set_rows(rows, self._workflow_id)
        self.workflowsChanged.emit()
        self._refresh_runs()
        self.refreshSchedules()

    @Slot()
    def refreshSchedules(self) -> None:
        """Read-only Schedule-Liste (aktives Projekt + global), über Schedule-Read-Port."""
        try:
            pid = self._port.get_active_project_id()
            raw = self._schedule_read_port.list_schedule_summaries(
                project_scope_id=pid,
                include_global=True,
            )
            rows: list[dict[str, object]] = [dict(x) for x in raw]
            self._schedules.set_rows(rows)
        except Exception:
            logger.exception("schedule summaries")
            self._schedules.set_rows([])

    @Slot(str)
    def setRunListScope(self, scope: str) -> None:
        s = (scope or "").strip().lower()
        if s not in (RUN_SCOPE_WORKFLOW, RUN_SCOPE_PROJECT, RUN_SCOPE_ALL):
            return
        if self._run_list_scope == s:
            return
        self._run_list_scope = s
        self.runListScopeChanged.emit()
        self._refresh_runs()

    @Slot(str)
    def setRunStatusFilter(self, status_value: str) -> None:
        v = (status_value or "").strip()
        new = v if v else None
        if self._run_status_filter == new:
            return
        self._run_status_filter = new
        self.runStatusFilterChanged.emit()
        self._refresh_runs()

    @Slot(str)
    def selectRun(self, run_id: str) -> None:
        rid = (run_id or "").strip()
        if not rid:
            self._clear_run_detail()
            return
        try:
            run = self._port.get_run(rid)
        except RunNotFoundError:
            self._set_error(f"Run {rid!r} nicht gefunden.")
            self._clear_run_detail()
            return
        except Exception as e:
            logger.exception("get_run")
            self._set_error(str(e))
            self._clear_run_detail()
            return
        self._set_error("")
        self._selected_run_id = rid
        self._runs.set_selected_run(rid)
        self._apply_run_detail(run)
        self.selectedRunIdChanged.emit()

    @Slot(str)
    def selectNodeRun(self, node_run_id: str) -> None:
        nid = (node_run_id or "").strip()
        if not nid or not self._current_run:
            self._node_runs.set_selected(None)
            self._selected_node_run_id = None
            self._node_run_input_json = ""
            self._node_run_output_json = ""
            self._node_run_error_text = ""
            self.selectedNodeRunDetailChanged.emit()
            return
        for nr in self._current_run.node_runs:
            if nr.node_run_id == nid:
                self._selected_node_run_id = nid
                self._node_runs.set_selected(nid)
                self._node_run_input_json = self._presenter.json_preview(
                    dict(nr.input_payload) if nr.input_payload else None
                )
                self._node_run_output_json = self._presenter.json_preview(
                    dict(nr.output_payload) if nr.output_payload else None
                )
                self._node_run_error_text = (nr.error_message or "").strip()
                self.selectedNodeRunDetailChanged.emit()
                return
        self._set_error(f"NodeRun {nid!r} nicht im aktuellen Run.")

    @Slot()
    def rerunSelectedRunSameInputs(self) -> None:
        if not self._selected_run_id:
            self._set_error("Kein Run ausgewählt.")
            return
        self._set_busy(True)
        try:
            new_run = self._port.start_run_from_previous(self._selected_run_id, None)
            self._set_error("")
            self._refresh_runs()
            self.selectRun(new_run.run_id)
        except IncompleteHistoricalRunError as e:
            self._set_error(str(e))
        except WorkflowValidationError as e:
            self._set_error("Validierung: " + "; ".join(e.errors[:8]))
        except WorkflowNotFoundError as e:
            self._set_error(str(e))
        except Exception as e:
            logger.exception("rerun")
            self._set_error(str(e))
        finally:
            self._set_busy(False)

    @Slot(str)
    def setRerunOverrideInputJson(self, json_text: str) -> None:
        t = json_text if json_text is not None else ""
        if self._rerun_override_input_json != t:
            self._rerun_override_input_json = t
            self.rerunOverrideInputJsonChanged.emit()

    @Slot()
    def syncRerunOverrideFromSelectedRun(self) -> None:
        """Übernimmt ``initial_input`` des gewählten Laufs als JSON (wie Re-Run-Dialog-Vorbelegung)."""
        if not self._current_run:
            self._set_error("Kein Run ausgewählt.")
            return
        preview = self._presenter.json_preview(dict(self._current_run.initial_input or {}), limit=8000)
        self.setRerunOverrideInputJson(preview)

    @Slot()
    def startRerunWithCommittedOverride(self) -> None:
        """
        Re-Run mit explizitem ``initial_input_override`` (Produkt: :meth:`WorkflowService.start_run_from_previous`).

        Nutzt dieselbe JSON-Objekt-Parsing-Semantik wie Test-Run / ``WorkflowInputDialog``.
        Leerer Text ist ungültig — nutzen Sie ``rerunSelectedRunSameInputs`` für „gleiche Eingaben“.
        """
        if not self._selected_run_id:
            self._set_error("Kein Run ausgewählt.")
            return
        raw = (self._rerun_override_input_json or "").strip()
        if not raw:
            self._set_error(
                "Re-Run-Override: JSON eingeben oder „Aus Run übernehmen“, "
                "sonst „Re-Run (gleiche Eingaben)“ verwenden."
            )
            return
        parsed, err = WorkflowStudioPresenter.parse_initial_input_json(self._rerun_override_input_json)
        if err:
            self._set_error(err)
            return
        if parsed is None:
            self._set_error("Ungültige Eingabe.")
            return
        self._set_busy(True)
        try:
            new_run = self._port.start_run_from_previous(self._selected_run_id, parsed)
            self._set_error("")
            self._refresh_runs()
            self.selectRun(new_run.run_id)
        except IncompleteHistoricalRunError as e:
            self._set_error(str(e))
        except WorkflowValidationError as e:
            self._set_error("Validierung: " + "; ".join(e.errors[:8]))
        except WorkflowNotFoundError as e:
            self._set_error(str(e))
        except Exception as e:
            logger.exception("rerun override")
            self._set_error(str(e))
        finally:
            self._set_busy(False)

    def _replace_workflow_selection(self, workflow_id: str) -> None:
        """Ersetzt den bearbeiteten Graph (kein Dirty-Check — nur nach Freigabe aufrufen)."""
        wid = (workflow_id or "").strip()
        if not wid:
            self._definition = None
            self._workflow_id = None
            self._nodes.set_graph([], None)
            self._edges.set_edges([])
            self._selected_node_id = None
            self._workflows.set_selected(None)
            self._clear_graph_dirty()
            self.selectedWorkflowChanged.emit()
            self.nodesChanged.emit()
            self.edgesChanged.emit()
            self.selectedNodeChanged.emit()
            self._clear_run_detail()
            self._refresh_runs()
            return
        try:
            raw = self._port.load_workflow(wid)
        except WorkflowNotFoundError:
            self._set_error(f"Workflow {wid!r} nicht gefunden.")
            return
        except Exception as e:
            self._set_error(str(e))
            return
        self._definition = WorkflowDefinition.from_dict(copy.deepcopy(raw.to_dict()))
        self._workflow_id = wid
        self._selected_node_id = None
        self._pending_edge_source = None
        self.pendingEdgeSourceChanged.emit()
        self._workflows.set_selected(wid)
        self._push_graph_models()
        self._clear_graph_dirty()
        self.selectedWorkflowChanged.emit()
        self.nodesChanged.emit()
        self.edgesChanged.emit()
        self.selectedNodeChanged.emit()
        self._set_error("")
        self._clear_run_detail()
        self._refresh_runs()

    @Slot(str)
    def requestSelectWorkflow(self, workflow_id: str) -> None:
        """QML: Wechsel der Liste — bei ``graphDirty`` Entscheidungszustand statt stillem Verwerfen."""
        wid = (workflow_id or "").strip()
        if wid == (self._workflow_id or ""):
            return
        if not self._graph_dirty:
            self._replace_workflow_selection(wid)
            return
        self._begin_graph_action(
            kind="switch_workflow",
            target_workflow_id=wid,
            deferred_context=None,
            prompt=(
                f"Ungespeicherte Graph-Änderungen. Vor dem Wechsel zu „{wid}“: "
                "speichern, verwerfen (lokale Änderungen an diesem Workflow gehen verloren) oder abbrechen."
            ),
        )

    @Slot()
    def resolveGraphActionDiscard(self) -> None:
        if not self._graph_action_pending:
            return
        kind = self._graph_action_kind
        target = self._graph_action_target_workflow_id
        deferred = self._deferred_context
        self._clear_graph_action()
        if kind == "switch_workflow":
            self._replace_workflow_selection(target)
            self.shellPendingContextClearSuggested.emit()
        elif kind == "apply_context":
            if not self._reload_current_workflow_from_disk():
                self.shellPendingContextClearSuggested.emit()
                return
            if deferred is not None:
                self._apply_parsed_context(deferred)
            else:
                self.shellPendingContextClearSuggested.emit()
        elif kind == "test_run":
            if not self._reload_current_workflow_from_disk():
                self.shellPendingContextClearSuggested.emit()
                return
            self._execute_test_run_parsed()
            self.shellPendingContextClearSuggested.emit()

    @Slot()
    def resolveGraphActionSave(self) -> None:
        if not self._graph_action_pending:
            return
        kind = self._graph_action_kind
        target = self._graph_action_target_workflow_id
        deferred = self._deferred_context
        if not self._definition or not self._workflow_id:
            self._clear_graph_action()
            self.shellPendingContextClearSuggested.emit()
            return
        try:
            vr = self._port.save_workflow(self._definition)
            if not vr.is_valid:
                self._set_error("Validierung: " + "; ".join(vr.errors[:5]))
                return
            self._clear_graph_dirty()
        except Exception as e:
            self._set_error(str(e))
            return
        self._clear_graph_action()
        if kind == "switch_workflow":
            self._replace_workflow_selection(target)
            self.shellPendingContextClearSuggested.emit()
        elif kind == "apply_context":
            if deferred is not None:
                self._apply_parsed_context(deferred)
            else:
                self.shellPendingContextClearSuggested.emit()
        elif kind == "test_run":
            self._execute_test_run_parsed()
            self.shellPendingContextClearSuggested.emit()

    @Slot()
    def resolveGraphActionCancel(self) -> None:
        """
        Bricht die offene Graph-Entscheidung ab.

        Kein ``shellPendingContextClearSuggested``: die Shell behält ``pendingContextJson``,
        damit Deep-Links / operations_context nicht still verworfen werden (erneutes
        ``consumeShellPendingContext`` z. B. nach erneutem Stage-Fokus liegt bei der Shell).
        """
        if not self._graph_action_pending:
            return
        kind = self._graph_action_kind
        self._clear_graph_action()
        if kind == "apply_context":
            self._set_error("Kontext-Navigation abgebrochen (ungespeicherte Graph-Änderungen).")
        elif kind == "switch_workflow":
            self._set_error("Workflow-Wechsel abgebrochen.")
        elif kind == "test_run":
            self._set_error("Test-Run abgebrochen.")

    def _apply_parsed_context(self, ctx: dict[str, object]) -> None:
        run_id = (str(ctx.get("workflow_ops_run_id") or "")).strip()
        wf_for_run = (str(ctx.get("workflow_ops_workflow_id") or "")).strip()
        if run_id:
            if wf_for_run and not self._graph_dirty:
                self._replace_workflow_selection(wf_for_run)
            else:
                self._run_list_scope = RUN_SCOPE_ALL
                self.runListScopeChanged.emit()
                self._refresh_runs()
            self.selectRun(run_id)
            self.shellPendingContextClearSuggested.emit()
            return
        if ctx.get("workflow_ops_scope") == "project":
            pid = self._port.get_active_project_id()
            self._list_project_scope_id = int(pid) if pid is not None else None
            self._run_list_scope = RUN_SCOPE_PROJECT
            self.runListScopeChanged.emit()
        else:
            self._list_project_scope_id = None
        sel_wf = (str(ctx.get("workflow_ops_select_workflow_id") or "")).strip()
        self.reload()
        if sel_wf and self._graph_dirty:
            self._begin_graph_action(
                kind="apply_context",
                target_workflow_id="",
                deferred_context=copy.deepcopy(ctx),
                prompt=(
                    f"Die Navigation soll den Workflow „{sel_wf}“ öffnen. "
                    "Ungespeicherte Graph-Änderungen: speichern, vom Server neu laden (verwerfen) oder abbrechen."
                ),
            )
            return
        if sel_wf:
            self._replace_workflow_selection(sel_wf)
        self.shellPendingContextClearSuggested.emit()

    def _execute_test_run_parsed(self) -> None:
        if not self._workflow_id or not self._definition:
            self._set_error("Kein Workflow geladen.")
            return
        parsed, err = WorkflowStudioPresenter.parse_initial_input_json(self._test_run_input_json)
        if err:
            self._set_error(err)
            return
        if parsed is None:
            self._set_error("Ungültige Eingabe.")
            return
        vr = self._port.validate_workflow(self._definition)
        if not vr.is_valid:
            self._set_error("Validierung: " + "; ".join(vr.errors[:8]))
            return
        self._set_busy(True)
        try:
            rid = self._port.start_run(self._workflow_id, parsed)
            self._set_error("")
            self._refresh_runs()
            self.selectRun(rid)
        except WorkflowValidationError as e:
            self._set_error("Validierung: " + "; ".join(e.errors[:8]))
        except Exception as e:
            logger.exception("test run")
            self._set_error(str(e))
        finally:
            self._set_busy(False)

    @Slot(str)
    def setTestRunInputJson(self, json_text: str) -> None:
        t = json_text if json_text is not None else ""
        if self._test_run_input_json != t:
            self._test_run_input_json = t
            self.testRunInputJsonChanged.emit()

    @Slot()
    def startTestRun(self) -> None:
        """Test-Run mit :attr:`testRunInputJson` (Semantik wie ``WorkflowInputDialog``)."""
        if not self._workflow_id or not self._definition:
            self._set_error("Kein Workflow geladen.")
            return
        if self._graph_dirty:
            self._begin_graph_action(
                kind="test_run",
                target_workflow_id="",
                deferred_context=None,
                prompt=(
                    "Ungespeicherte Graph-Änderungen vor dem Test-Run: speichern, "
                    "verwerfen (Neuladen vom Server) oder abbrechen."
                ),
            )
            return
        self._execute_test_run_parsed()

    def _push_graph_models(self) -> None:
        if not self._definition:
            self._nodes.set_graph([], None)
            self._edges.set_edges([])
            return
        nrows: list[dict[str, object]] = []
        for n in self._definition.nodes:
            x, y = 0.0, 0.0
            if n.position:
                x = float(n.position.get("x", 0))
                y = float(n.position.get("y", 0))
            nrows.append(
                {
                    "nodeId": n.node_id,
                    "title": n.title or n.node_id,
                    "roleKey": _node_role_key(n.node_type),
                    "posX": x,
                    "posY": y,
                }
            )
        self._nodes.set_graph(nrows, self._selected_node_id)
        self._rebuild_edge_geometry()

    def _rebuild_edge_geometry(self) -> None:
        if not self._definition:
            self._edges.set_edges([])
            return
        pos: dict[str, tuple[float, float]] = {}
        for n in self._definition.nodes:
            x, y = 0.0, 0.0
            if n.position:
                x = float(n.position.get("x", 0))
                y = float(n.position.get("y", 0))
            pos[n.node_id] = (x, y)
        erows: list[dict[str, object]] = []
        for e in self._definition.edges:
            s = pos.get(e.source_node_id)
            t = pos.get(e.target_node_id)
            if not s or not t:
                continue
            sx, sy = s[0] + NODE_W, s[1] + NODE_H / 2
            tx, ty = t[0], t[1] + NODE_H / 2
            fk = effective_edge_flow_kind(e)
            erows.append(
                {
                    "edgeId": e.edge_id,
                    "sx": sx,
                    "sy": sy,
                    "tx": tx,
                    "ty": ty,
                    "flowKind": fk,
                }
            )
        self._edges.set_edges(erows)

    @Slot(str)
    def selectNode(self, node_id: str) -> None:
        nid = (node_id or "").strip() or None
        self._selected_node_id = nid
        self._nodes.set_selected(nid)
        self.selectedNodeChanged.emit()

    @Slot(str, float, float)
    def moveNode(self, node_id: str, x: float, y: float) -> None:
        if not self._definition:
            return
        node = self._definition.node_by_id(node_id)
        if node is None:
            return
        node.position = {"x": float(x), "y": float(y)}
        self._nodes.update_node_pos(node_id, float(x), float(y))
        self._rebuild_edge_geometry()
        self.edgesChanged.emit()
        self._mark_graph_dirty()

    @Slot(str)
    def addNode(self, role_key: str) -> None:
        if not self._definition:
            self._set_error("Kein Workflow geladen.")
            return
        rk = (role_key or "agent").strip().lower()
        ntype = _ROLE_TO_TYPE.get(rk, "noop")
        nid = f"n_{uuid.uuid4().hex[:8]}"
        base_x = 80.0 + len(self._definition.nodes) * 24
        base_y = 80.0 + len(self._definition.nodes) * 20
        title = {"agent": "Agent", "prompt": "Prompt", "tool": "Tool", "model": "Modell", "memory": "Memory", "condition": "Bedingung"}.get(
            rk, "Knoten"
        )
        self._definition.nodes.append(
            WorkflowNode(nid, ntype, title=title, position={"x": base_x, "y": base_y})
        )
        self._push_graph_models()
        self.nodesChanged.emit()
        self.edgesChanged.emit()
        self.selectNode(nid)
        self._set_error("")
        self._mark_graph_dirty()

    @Slot(str, str, str)
    def connectNodes(self, source_id: str, target_id: str, flow_kind: str) -> None:
        if not self._definition:
            self._set_error("Kein Workflow geladen.")
            return
        a = (source_id or "").strip()
        b = (target_id or "").strip()
        if not a or not b or a == b:
            return
        if self._definition.node_by_id(a) is None or self._definition.node_by_id(b) is None:
            self._set_error("Unbekannte Knoten-ID.")
            return
        if any(e.source_node_id == a and e.target_node_id == b for e in self._definition.edges):
            return
        fk = (flow_kind or "data").strip().lower()
        flow = fk if fk in ("data", "control") else "data"
        eid = f"e_{uuid.uuid4().hex[:10]}"
        self._definition.edges.append(
            WorkflowEdge(eid, a, b, flow_kind=flow)
        )
        self._rebuild_edge_geometry()
        self.edgesChanged.emit()
        self._set_error("")
        self._mark_graph_dirty()

    @Slot()
    def startEdgeFromSelectedNode(self) -> None:
        if not self._selected_node_id:
            self._set_error("Kein Knoten gewählt.")
            return
        self._pending_edge_source = self._selected_node_id
        self.pendingEdgeSourceChanged.emit()

    @Slot(str)
    def completeEdgeToSelectedNode(self, flow_kind: str) -> None:
        if not self._pending_edge_source or not self._selected_node_id:
            self._set_error("Quelle und Ziel wählen (Zuerst „Kante von Auswahl“, dann Ziel-Knoten).")
            return
        self.connectNodes(self._pending_edge_source, self._selected_node_id, flow_kind)
        self._pending_edge_source = None
        self.pendingEdgeSourceChanged.emit()

    @Slot()
    def cancelPendingEdge(self) -> None:
        self._pending_edge_source = None
        self.pendingEdgeSourceChanged.emit()

    @Slot()
    def saveGraph(self) -> None:
        if not self._definition or not self._workflow_id:
            self._set_error("Kein Workflow geladen.")
            return
        try:
            vr = self._port.save_workflow(self._definition)
            if not vr.is_valid:
                self._set_error("Validierung: " + "; ".join(vr.errors[:5]))
                return
            self._set_error("")
            self._clear_graph_dirty()
        except Exception as e:
            self._set_error(str(e))

    @Slot()
    def runWorkflow(self) -> None:
        """Schnellstart mit leerem ``initial_input`` (wie bisher); zentraler Pfad = :meth:`startTestRun`."""
        self.setTestRunInputJson("{}")
        self.startTestRun()

    @Slot(str)
    def applyShellPendingContextJson(self, json_str: str) -> None:
        """
        Gleiche Schlüssel wie ``WorkflowsWorkspace.open_with_context`` (operations_context).

        Bei blockierender offener Graph-Aktion wird nichts angewendet; die Shell soll das
        Pending-JSON behalten. Nach Speichern/Verwerfen (und erfolgreicher Kontext-Anwendung)
        signalisiert ``shellPendingContextClearSuggested`` das Leeren — nicht nach „Abbrechen“.
        """
        if self._graph_action_pending:
            self._set_error(
                "Navigation blockiert: bitte zuerst Speichern, Verwerfen oder Abbrechen bei der offenen Graph-Entscheidung."
            )
            return
        raw = (json_str or "").strip()
        if not raw:
            return
        try:
            ctx = json.loads(raw)
        except json.JSONDecodeError:
            return
        if not isinstance(ctx, dict):
            return
        self._apply_parsed_context(ctx)


def build_workflow_viewmodel() -> WorkflowStudioViewModel:
    return WorkflowStudioViewModel()
