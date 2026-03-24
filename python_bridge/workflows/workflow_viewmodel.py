"""
QML-Kontextobjekt ``workflowStudio``: Workflows, Graph, Inspector, Run-Historie.

Slots: selectWorkflow, addNode, connectNodes, moveNode, selectNode, runWorkflow, reload
"""

from __future__ import annotations

import copy
import logging
import uuid
from datetime import datetime

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.services.workflow_service import WorkflowNotFoundError
from app.ui_application.adapters.service_qml_workflow_canvas_adapter import ServiceQmlWorkflowCanvasAdapter
from app.ui_application.ports.qml_workflow_canvas_port import QmlWorkflowCanvasPort
from app.workflows.models.definition import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowNode,
    effective_edge_flow_kind,
)
from app.workflows.models.run_summary import WorkflowRunSummary

from python_bridge.workflows.workflow_models import (
    WorkflowGraphEdgeModel,
    WorkflowGraphNodeModel,
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


def _fmt_run_duration(started_at: datetime | None, finished_at: datetime | None) -> str:
    if started_at is None or finished_at is None:
        return "—"
    try:
        sec = int((finished_at - started_at).total_seconds())
    except Exception:
        return "—"
    if sec < 0:
        return "—"
    if sec < 1:
        return "<1s"
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


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

    def __init__(
        self,
        port: QmlWorkflowCanvasPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlWorkflowCanvasPort = port or ServiceQmlWorkflowCanvasAdapter()
        self._workflows = WorkflowSummaryListModel(self)
        self._nodes = WorkflowGraphNodeModel(self)
        self._edges = WorkflowGraphEdgeModel(self)
        self._runs = WorkflowRunHistoryModel(self)
        self._definition: WorkflowDefinition | None = None
        self._workflow_id: str | None = None
        self._selected_node_id: str | None = None
        self._last_error = ""
        self._run_busy = False
        self._pending_edge_source: str | None = None

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

    @Slot()
    def reload(self) -> None:
        self._set_error("")
        try:
            items = self._port.list_workflows(project_scope_id=None, include_global=True)
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
        if self._workflow_id:
            self._refresh_runs()

    def _refresh_runs(self) -> None:
        if not self._workflow_id:
            self._runs.set_rows([])
            self.runsChanged.emit()
            return
        try:
            sums: list[WorkflowRunSummary] = self._port.list_run_summaries(workflow_id=self._workflow_id)
        except Exception:
            logger.exception("run summaries")
            sums = []
        rows: list[dict[str, object]] = []
        for s in sums[:50]:
            rows.append(
                {
                    "runId": s.run_id,
                    "status": s.status,
                    "duration": _fmt_run_duration(s.started_at, s.finished_at),
                    "started": s.started_at.isoformat() if s.started_at else "",
                }
            )
        self._runs.set_rows(rows)
        self.runsChanged.emit()

    @Slot(str)
    def selectWorkflow(self, workflow_id: str) -> None:
        wid = (workflow_id or "").strip()
        if not wid:
            self._definition = None
            self._workflow_id = None
            self._nodes.set_graph([], None)
            self._edges.set_edges([])
            self._selected_node_id = None
            self._workflows.set_selected(None)
            self.selectedWorkflowChanged.emit()
            self.nodesChanged.emit()
            self.edgesChanged.emit()
            self.selectedNodeChanged.emit()
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
        self.selectedWorkflowChanged.emit()
        self.nodesChanged.emit()
        self.edgesChanged.emit()
        self.selectedNodeChanged.emit()
        self._set_error("")
        self._refresh_runs()

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
        except Exception as e:
            self._set_error(str(e))

    @Slot()
    def runWorkflow(self) -> None:
        if not self._workflow_id or not self._definition:
            self._set_error("Kein Workflow geladen.")
            return
        self._set_busy(True)
        try:
            self._port.save_workflow(self._definition)
            self._port.start_run(self._workflow_id, {})
            self._set_error("")
            self._refresh_runs()
        except Exception as e:
            logger.exception("run workflow")
            self._set_error(str(e))
        finally:
            self._set_busy(False)


def build_workflow_viewmodel() -> WorkflowStudioViewModel:
    return WorkflowStudioViewModel()
