"""Szene: projiziert WorkflowDefinition auf Items."""

from __future__ import annotations

import uuid
from typing import Dict, Optional

from PySide6.QtCore import QRectF, Signal
from PySide6.QtWidgets import QGraphicsScene

from app.gui.domains.operations.workflows.canvas.canvas_layout import ensure_missing_positions, write_position
from app.gui.domains.operations.workflows.canvas.workflow_edge_item import WorkflowEdgeItem
from app.gui.domains.operations.workflows.canvas.workflow_node_item import WorkflowNodeItem
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.status import NodeRunStatus


class WorkflowGraphicsScene(QGraphicsScene):
    """Baut Knoten/Kanten aus derselben Definition-Instanz wie der Tabellen-Editor."""

    node_selected = Signal(object)  # Optional[str]
    definition_user_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._wf: Optional[WorkflowDefinition] = None
        self._node_items: Dict[str, WorkflowNodeItem] = {}
        self._edge_items: Dict[str, WorkflowEdgeItem] = {}
        self._connect_mode = False
        self._connect_source: Optional[str] = None
        self._suppress_selection_emit = False
        self.selectionChanged.connect(self._on_scene_selection_changed)
        self._run_overlay: Dict[str, Optional[NodeRunStatus]] = {}

    @property
    def connect_mode(self) -> bool:
        return self._connect_mode

    def set_connect_mode(self, active: bool) -> None:
        self._connect_mode = active
        self._connect_source = None

    def set_definition(self, wf: Optional[WorkflowDefinition]) -> int:
        self._wf = wf
        return self.rebuild()

    def rebuild(self) -> int:
        """
        Returns:
            Anzahl Knoten, denen in diesem Rebuild per Auto-Layout eine Position gegeben wurde.
            Bei > 0 wird genau einmal definition_user_modified emittiert (Dirty / Tabellen-Sync).
        """
        self.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._connect_source = None
        if self._wf is None:
            self._run_overlay.clear()
            return 0
        auto_filled = ensure_missing_positions(self._wf)
        for n in self._wf.nodes:
            it = WorkflowNodeItem(n.node_id, n.title, n.node_type)
            x, y = 0.0, 0.0
            if n.position:
                x = float(n.position.get("x", 0))
                y = float(n.position.get("y", 0))
            it.setPos(x, y)
            it.position_committed.connect(self._on_node_position_committed)
            it.connect_pick_requested.connect(self._on_connect_pick)
            self.addItem(it)
            self._node_items[n.node_id] = it
        for e in self._wf.edges:
            ei = WorkflowEdgeItem(
                e.edge_id,
                e.source_node_id,
                e.target_node_id,
                self._on_edge_delete_requested,
            )
            self.addItem(ei)
            self._edge_items[e.edge_id] = ei
            ei.update_geometry(
                self._node_items.get(e.source_node_id),
                self._node_items.get(e.target_node_id),
            )
        if auto_filled > 0:
            self.definition_user_modified.emit()
        self._apply_run_overlay_to_items()
        return auto_filled

    def set_node_run_overlay(self, mapping: Optional[Dict[str, Optional[NodeRunStatus]]]) -> None:
        self._run_overlay.clear()
        if mapping:
            self._run_overlay.update(mapping)
        self._apply_run_overlay_to_items()

    def _apply_run_overlay_to_items(self) -> None:
        for nid, it in self._node_items.items():
            it.set_run_status_overlay(self._run_overlay.get(nid))

    def update_incident_edges(self, node_id: str) -> None:
        for e in self._wf.edges if self._wf else []:
            if e.source_node_id != node_id and e.target_node_id != node_id:
                continue
            ei = self._edge_items.get(e.edge_id)
            if ei:
                ei.update_geometry(
                    self._node_items.get(e.source_node_id),
                    self._node_items.get(e.target_node_id),
                )

    def _on_node_position_committed(self, node_id: str, x: float, y: float) -> None:
        if not self._wf:
            return
        node = next((n for n in self._wf.nodes if n.node_id == node_id), None)
        if node:
            write_position(node, x, y)
        self.definition_user_modified.emit()

    def _on_connect_pick(self, node_id: str) -> None:
        if not self._connect_mode or not self._wf:
            return
        if self._connect_source is None:
            self._connect_source = node_id
            return
        a, b = self._connect_source, node_id
        self._connect_source = None
        if a == b:
            return
        if any(
            e.source_node_id == a and e.target_node_id == b for e in self._wf.edges
        ):
            return
        eid = f"e_{uuid.uuid4().hex[:10]}"
        self._wf.edges.append(WorkflowEdge(eid, a, b))
        self.definition_user_modified.emit()
        self.rebuild()  # Auto-Layout: kein zweites Signal (auto_filled == 0)
        self.select_node_programmatic(b)

    def _on_edge_delete_requested(self, edge_id: str) -> None:
        if not self._wf:
            return
        self._wf.edges = [e for e in self._wf.edges if e.edge_id != edge_id]
        self.definition_user_modified.emit()
        self.rebuild()  # Auto-Layout: kein zweites Signal (auto_filled == 0)

    def _on_scene_selection_changed(self) -> None:
        if self._suppress_selection_emit:
            return
        sel = self.selectedItems()
        for it in sel:
            if isinstance(it, WorkflowNodeItem):
                self.node_selected.emit(it.node_id)
                return
        self.node_selected.emit(None)

    def select_node_programmatic(self, node_id: Optional[str]) -> None:
        self._suppress_selection_emit = True
        self.clearSelection()
        if node_id and node_id in self._node_items:
            self._node_items[node_id].setSelected(True)
        self._suppress_selection_emit = False

    def refresh_node_labels(self) -> None:
        """Nach Inspector-/Tabellenänderung ohne Positions-Reset."""
        if not self._wf:
            return
        for n in self._wf.nodes:
            it = self._node_items.get(n.node_id)
            if it:
                it.set_labels(n.title, n.node_type)
                it.set_run_status_overlay(self._run_overlay.get(n.node_id))
        for e in self._wf.edges:
            ei = self._edge_items.get(e.edge_id)
            if ei:
                ei.update_geometry(
                    self._node_items.get(e.source_node_id),
                    self._node_items.get(e.target_node_id),
                )

    def fit_nodes_rect(self, padding: float = 40) -> QRectF:
        """Bounding-Rect aller Knoten für Fit-in-View."""
        if not self._node_items:
            return QRectF(0, 0, 400, 300)
        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        for it in self._node_items.values():
            r = it.sceneBoundingRect()
            xmin = min(xmin, r.left())
            ymin = min(ymin, r.top())
            xmax = max(xmax, r.right())
            ymax = max(ymax, r.bottom())
        return QRectF(xmin - padding, ymin - padding, xmax - xmin + 2 * padding, ymax - ymin + 2 * padding)
