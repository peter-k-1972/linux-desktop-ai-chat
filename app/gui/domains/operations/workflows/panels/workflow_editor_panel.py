"""Tabellarischer Editor für WorkflowDefinition."""

from __future__ import annotations

import uuid
from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.gui.domains.operations.workflows.canvas.workflow_canvas_widget import WorkflowCanvasWidget
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.status import NodeRunStatus


class WorkflowEditorPanel(QFrame):
    """Kopfdaten, Prozessdiagramm (Canvas) und optional Tabellen für Knoten/Kanten."""

    content_modified = Signal()
    node_selection_changed = Signal(object)  # Optional[str]
    save_requested = Signal()
    validate_requested = Signal()
    test_run_requested = Signal()
    reload_requested = Signal()
    export_json_requested = Signal()

    def __init__(self, parent=None, *, planning_board: bool = False):
        super().__init__(parent)
        self.setObjectName("workflowEditorPanel")
        self._planning_board = planning_board
        self._wf: Optional[WorkflowDefinition] = None
        self._loading = False
        self._suppress_selection = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        head = QGroupBox("Workflow")
        hl = QGridLayout(head)
        self._name = QLineEdit()
        self._name.editingFinished.connect(self._on_meta_changed)
        hl.addWidget(QLabel("Name:"), 0, 0)
        hl.addWidget(self._name, 0, 1)
        self._desc = QTextEdit()
        self._desc.setMaximumHeight(64)
        self._desc.textChanged.connect(self._on_desc_changed)
        hl.addWidget(QLabel("Beschreibung:"), 1, 0)
        hl.addWidget(self._desc, 1, 1)
        self._lbl_id = QLabel("—")
        self._lbl_ver = QLabel("—")
        self._lbl_status = QLabel("—")
        self._lbl_schema = QLabel("—")
        hl.addWidget(QLabel("workflow_id:"), 2, 0)
        hl.addWidget(self._lbl_id, 2, 1)
        hl.addWidget(QLabel("Version:"), 3, 0)
        hl.addWidget(self._lbl_ver, 3, 1)
        hl.addWidget(QLabel("Status:"), 4, 0)
        hl.addWidget(self._lbl_status, 4, 1)
        hl.addWidget(QLabel("schema_version:"), 5, 0)
        hl.addWidget(self._lbl_schema, 5, 1)
        self._project_combo = QComboBox()
        self._project_combo.setToolTip(
            "Global = für alle Projekte nutzbar. Sonst nur im gewählten Projekt in der Liste sichtbar "
            "(bei aktivem Projekt-Filter)."
        )
        self._project_combo.currentIndexChanged.connect(self._on_project_combo_changed)
        hl.addWidget(QLabel("Projekt:"), 6, 0)
        hl.addWidget(self._project_combo, 6, 1)
        layout.addWidget(head)

        tb = QHBoxLayout()
        for label, sig in [
            ("Speichern", self.save_requested),
            ("Validieren", self.validate_requested),
            ("Test-Run", self.test_run_requested),
            ("Verwerfen", self.reload_requested),
            ("JSON exportieren", self.export_json_requested),
        ]:
            b = QPushButton(label)
            b.clicked.connect(sig.emit)
            tb.addWidget(b)
        tb.addStretch()
        layout.addLayout(tb)

        self._canvas = WorkflowCanvasWidget(self)
        self._canvas.node_selected.connect(self._on_canvas_node_selected)
        self._canvas.definition_user_modified.connect(self._on_canvas_definition_modified)

        nodes_box = QGroupBox("Knoten")
        nv = QVBoxLayout(nodes_box)
        nbtn = QHBoxLayout()
        self._btn_add_n = QPushButton("Knoten hinzufügen")
        self._btn_add_n.clicked.connect(self._add_node)
        self._btn_rm_n = QPushButton("Knoten entfernen")
        self._btn_rm_n.clicked.connect(self._remove_node)
        self._btn_dup_n = QPushButton("Knoten duplizieren")
        self._btn_dup_n.clicked.connect(self._dup_node)
        for b in (self._btn_add_n, self._btn_rm_n, self._btn_dup_n):
            nbtn.addWidget(b)
        nbtn.addStretch()
        nv.addLayout(nbtn)
        self._nodes = QTableWidget(0, 4)
        self._nodes.setHorizontalHeaderLabels(["node_id", "node_type", "title", "aktiv"])
        self._nodes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._nodes.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._nodes.itemChanged.connect(self._on_node_cell_changed)
        self._nodes.itemSelectionChanged.connect(self._on_node_sel)
        nv.addWidget(self._nodes)

        edges_box = QGroupBox("Kanten")
        ev = QVBoxLayout(edges_box)
        ebtn = QHBoxLayout()
        self._btn_add_e = QPushButton("Kante hinzufügen")
        self._btn_add_e.clicked.connect(self._add_edge)
        self._btn_rm_e = QPushButton("Kante entfernen")
        self._btn_rm_e.clicked.connect(self._remove_edge)
        for b in (self._btn_add_e, self._btn_rm_e):
            ebtn.addWidget(b)
        ebtn.addStretch()
        ev.addLayout(ebtn)
        self._edges = QTableWidget(0, 7)
        self._edges.setHorizontalHeaderLabels(
            [
                "edge_id",
                "source_node_id",
                "target_node_id",
                "source_port",
                "target_port",
                "condition",
                "flow_kind",
            ]
        )
        self._edges.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._edges.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._edges.itemChanged.connect(self._on_edge_cell_changed)
        ev.addWidget(self._edges)

        self._tables_wrap = QWidget()
        tables_layout = QVBoxLayout(self._tables_wrap)
        tables_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.addWidget(nodes_box, 2)
        tables_layout.addWidget(edges_box, 2)

        if self._planning_board:
            layout.addWidget(self._canvas, 1)
            leg_row = QHBoxLayout()
            leg = QLabel(
                "<span style='color:#0d9488;font-weight:600'>■</span> Datenfluss &nbsp;&nbsp;"
                "<span style='color:#ea580c;font-weight:600'>┅</span> Kontrollfluss &nbsp;&nbsp;"
                "<span style='color:#64748b'>Knoten: Agent · Prompt · Tool · Modell · …</span>"
            )
            leg.setTextFormat(Qt.TextFormat.RichText)
            leg.setWordWrap(True)
            leg_row.addWidget(leg, 1)
            self._btn_open_tables = QPushButton("Knoten & Kanten (Tabellen)…")
            self._btn_open_tables.clicked.connect(self._open_tables_dialog)
            leg_row.addWidget(self._btn_open_tables, 0, Qt.AlignmentFlag.AlignRight)
            layout.addLayout(leg_row)
        else:
            self._tabs = QTabWidget()
            self._tabs.addTab(self._canvas, "Graph")
            self._tabs.addTab(self._tables_wrap, "Tabellen")
            layout.addWidget(self._tabs, 1)

    def _open_tables_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Knoten & Kanten")
        dlg.resize(920, 560)
        lay = QVBoxLayout(dlg)
        lay.addWidget(self._tables_wrap)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        bb.rejected.connect(dlg.reject)
        lay.addWidget(bb)
        dlg.exec()
        if self._planning_board:
            self._tables_wrap.setParent(self)

    def _on_meta_changed(self) -> None:
        if self._loading or not self._wf:
            return
        self._wf.name = self._name.text().strip() or self._wf.workflow_id
        self.content_modified.emit()

    def _on_desc_changed(self) -> None:
        if self._loading or not self._wf:
            return
        self._wf.description = self._desc.toPlainText().strip()
        self.content_modified.emit()

    def _on_project_combo_changed(self, _index: int) -> None:
        if self._loading or not self._wf:
            return
        pid = self._project_combo.currentData()
        self._wf.project_id = None if pid is None else int(pid)
        self.content_modified.emit()

    def _populate_project_combo(self, wf: Optional[WorkflowDefinition]) -> None:
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        self._project_combo.addItem("Global (kein Projekt)", None)
        try:
            from app.services.project_service import get_project_service

            for p in get_project_service().list_projects():
                pid = p.get("project_id")
                if pid is None:
                    continue
                name = (p.get("name") or "").strip() or f"Projekt {pid}"
                self._project_combo.addItem(name, int(pid))
        except Exception:
            pass
        target = wf.project_id if wf else None
        for i in range(self._project_combo.count()):
            if self._project_combo.itemData(i) == target:
                self._project_combo.setCurrentIndex(i)
                break
        self._project_combo.blockSignals(False)

    def set_definition(self, wf: Optional[WorkflowDefinition]) -> int:
        """
        Returns:
            Anzahl Knoten, die im Canvas-Rebuild per Auto-Layout eine Position erhielten.
            0 = keine neue Positions-Mutation durch den Rebuild (Workspace darf „clean“ setzen).
        """
        self._wf = wf
        self._loading = True
        self._nodes.blockSignals(True)
        self._edges.blockSignals(True)
        if not wf:
            self._name.clear()
            self._desc.clear()
            self._lbl_id.setText("—")
            self._lbl_ver.setText("—")
            self._lbl_status.setText("—")
            self._lbl_schema.setText("—")
            self._populate_project_combo(None)
            self._nodes.setRowCount(0)
            self._edges.setRowCount(0)
            self._nodes.blockSignals(False)
            self._edges.blockSignals(False)
            self._loading = False
            self._canvas.set_definition(None)
            return 0
        self._name.setText(wf.name)
        self._desc.setPlainText(wf.description)
        self._lbl_id.setText(wf.workflow_id)
        self._lbl_ver.setText(str(wf.version))
        self._lbl_status.setText(wf.status.value)
        self._lbl_schema.setText(str(wf.schema_version))
        self._populate_project_combo(wf)

        self._nodes.setRowCount(0)
        for n in wf.nodes:
            r = self._nodes.rowCount()
            self._nodes.insertRow(r)
            self._nodes.setItem(r, 0, QTableWidgetItem(n.node_id))
            self._nodes.setItem(r, 1, QTableWidgetItem(n.node_type))
            self._nodes.setItem(r, 2, QTableWidgetItem(n.title))
            chk = QTableWidgetItem()
            chk.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )
            chk.setCheckState(
                Qt.CheckState.Checked if n.is_enabled else Qt.CheckState.Unchecked
            )
            self._nodes.setItem(r, 3, chk)

        self._edges.setRowCount(0)
        for e in wf.edges:
            r = self._edges.rowCount()
            self._edges.insertRow(r)
            self._edges.setItem(r, 0, QTableWidgetItem(e.edge_id))
            self._edges.setItem(r, 1, QTableWidgetItem(e.source_node_id))
            self._edges.setItem(r, 2, QTableWidgetItem(e.target_node_id))
            self._edges.setItem(r, 3, QTableWidgetItem(e.source_port or ""))
            self._edges.setItem(r, 4, QTableWidgetItem(e.target_port or ""))
            self._edges.setItem(r, 5, QTableWidgetItem(e.condition or ""))
            fk = e.flow_kind or ""
            self._edges.setItem(r, 6, QTableWidgetItem(fk))

        self._nodes.resizeColumnsToContents()
        self._edges.resizeColumnsToContents()
        self._nodes.blockSignals(False)
        self._edges.blockSignals(False)
        self._loading = False
        return self._canvas.set_definition(wf)

    def refresh_header_labels(self) -> None:
        if self._wf:
            self._lbl_ver.setText(str(self._wf.version))
            self._lbl_status.setText(self._wf.status.value)
            self._lbl_schema.setText(str(self._wf.schema_version))

    def set_run_node_status_overlay(self, mapping: Optional[Dict[str, Optional[NodeRunStatus]]]) -> None:
        self._canvas.set_node_run_status_overlay(mapping)

    def select_node_by_id(self, node_id: Optional[str]) -> None:
        if not node_id or not self._wf:
            self._select_node_row(-1)
            return
        for i, n in enumerate(self._wf.nodes):
            if n.node_id == node_id:
                self._select_node_row(i)
                return
        self._select_node_row(-1)

    def _on_node_cell_changed(self, item: QTableWidgetItem) -> None:
        if self._loading or not self._wf:
            return
        row = item.row()
        if row >= len(self._wf.nodes):
            return
        n = self._wf.nodes[row]
        col = item.column()
        if col == 0:
            n.node_id = item.text().strip()
        elif col == 1:
            n.node_type = item.text().strip()
        elif col == 2:
            n.title = item.text().strip()
        elif col == 3:
            n.is_enabled = item.checkState() == Qt.CheckState.Checked
        self.content_modified.emit()
        self._canvas.reload_from_model()
        self._canvas.select_node_programmatic(self.selected_node_id())

    def _on_edge_cell_changed(self, item: QTableWidgetItem) -> None:
        if self._loading or not self._wf:
            return
        row = item.row()
        if row >= len(self._wf.edges):
            return
        e = self._wf.edges[row]
        col = item.column()
        val = item.text().strip()
        if col == 0:
            e.edge_id = val
        elif col == 1:
            e.source_node_id = val
        elif col == 2:
            e.target_node_id = val
        elif col == 3:
            e.source_port = val or None
        elif col == 4:
            e.target_port = val or None
        elif col == 5:
            e.condition = val or None
        elif col == 6:
            v = val.lower()
            e.flow_kind = v if v in ("data", "control") else None
        else:
            return
        self.content_modified.emit()
        self._canvas.reload_from_model()
        self._canvas.select_node_programmatic(self.selected_node_id())

    def _add_node(self) -> None:
        if not self._wf:
            return
        nid = f"n_{uuid.uuid4().hex[:8]}"
        self._wf.nodes.append(WorkflowNode(nid, "noop", title=nid))
        self.set_definition(self._wf)
        self._select_node_row(len(self._wf.nodes) - 1)
        self.content_modified.emit()

    def _remove_node(self) -> None:
        if not self._wf:
            return
        row = self._nodes.currentRow()
        if row < 0 or row >= len(self._wf.nodes):
            return
        nid = self._wf.nodes[row].node_id
        self._wf.nodes.pop(row)
        self._wf.edges = [
            e
            for e in self._wf.edges
            if e.source_node_id != nid and e.target_node_id != nid
        ]
        self.set_definition(self._wf)
        self.node_selection_changed.emit(None)
        self.content_modified.emit()

    def _dup_node(self) -> None:
        if not self._wf:
            return
        row = self._nodes.currentRow()
        if row < 0 or row >= len(self._wf.nodes):
            return
        src = self._wf.nodes[row]
        import copy

        new_id = f"{src.node_id}_copy_{uuid.uuid4().hex[:6]}"
        dup = WorkflowNode(
            new_id,
            src.node_type,
            title=src.title + " (Kopie)",
            description=src.description,
            config=copy.deepcopy(src.config),
            position=copy.deepcopy(src.position) if src.position else None,
            is_enabled=src.is_enabled,
        )
        self._wf.nodes.insert(row + 1, dup)
        self.set_definition(self._wf)
        self._select_node_row(row + 1)
        self.content_modified.emit()

    def _add_edge(self) -> None:
        if not self._wf:
            return
        eid = f"e_{uuid.uuid4().hex[:8]}"
        self._wf.edges.append(WorkflowEdge(eid, "", ""))
        self.set_definition(self._wf)
        self.content_modified.emit()

    def _remove_edge(self) -> None:
        if not self._wf:
            return
        row = self._edges.currentRow()
        if row < 0 or row >= len(self._wf.edges):
            return
        self._wf.edges.pop(row)
        self.set_definition(self._wf)
        self.content_modified.emit()

    def _select_node_row(self, row: int) -> None:
        self._suppress_selection = True
        if row < 0:
            self._nodes.clearSelection()
        else:
            self._nodes.selectRow(row)
        self._suppress_selection = False
        self._emit_node_sel()
        self._sync_canvas_selection_from_table()

    def _sync_canvas_selection_from_table(self) -> None:
        self._canvas.select_node_programmatic(self.selected_node_id())

    def _on_canvas_node_selected(self, node_id: object) -> None:
        if not self._wf:
            self._select_node_row(-1)
            return
        nid = node_id if isinstance(node_id, str) else None
        if nid is None:
            self._select_node_row(-1)
            return
        for i, n in enumerate(self._wf.nodes):
            if n.node_id == nid:
                self._select_node_row(i)
                return
        self._select_node_row(-1)

    def _on_canvas_definition_modified(self) -> None:
        self.content_modified.emit()
        self._repopulate_edges_table()

    def _repopulate_edges_table(self) -> None:
        if not self._wf:
            self._edges.blockSignals(True)
            self._edges.setRowCount(0)
            self._edges.blockSignals(False)
            return
        self._edges.blockSignals(True)
        self._edges.setRowCount(0)
        for e in self._wf.edges:
            r = self._edges.rowCount()
            self._edges.insertRow(r)
            self._edges.setItem(r, 0, QTableWidgetItem(e.edge_id))
            self._edges.setItem(r, 1, QTableWidgetItem(e.source_node_id))
            self._edges.setItem(r, 2, QTableWidgetItem(e.target_node_id))
            self._edges.setItem(r, 3, QTableWidgetItem(e.source_port or ""))
            self._edges.setItem(r, 4, QTableWidgetItem(e.target_port or ""))
            self._edges.setItem(r, 5, QTableWidgetItem(e.condition or ""))
            self._edges.setItem(r, 6, QTableWidgetItem(e.flow_kind or ""))
        self._edges.resizeColumnsToContents()
        self._edges.blockSignals(False)

    def _on_node_sel(self) -> None:
        if self._suppress_selection:
            return
        self._emit_node_sel()
        self._sync_canvas_selection_from_table()

    def _emit_node_sel(self) -> None:
        row = self._nodes.currentRow()
        if row < 0 or not self._wf or row >= len(self._wf.nodes):
            self.node_selection_changed.emit(None)
            return
        self.node_selection_changed.emit(self._wf.nodes[row].node_id)

    def selected_node_id(self) -> Optional[str]:
        row = self._nodes.currentRow()
        if not self._wf or row < 0 or row >= len(self._wf.nodes):
            return None
        return self._wf.nodes[row].node_id

    def apply_inspector_to_model(
        self,
        old_node_id: str,
        new_node_id: str,
        node_type: str,
        title: str,
        description: str,
        is_enabled: bool,
        config: dict,
    ) -> Optional[str]:
        """Schreibt Inspector-Felder in den Knoten. Bei node_id-Wechsel Kanten anpassen."""
        if not self._wf:
            return "Kein Workflow geladen."
        node = next((n for n in self._wf.nodes if n.node_id == old_node_id), None)
        if node is None:
            return f"Knoten {old_node_id!r} nicht gefunden."
        new_id = new_node_id.strip()
        if not new_id:
            return "node_id darf nicht leer sein."
        if new_id != old_node_id:
            if any(n.node_id == new_id for n in self._wf.nodes if n is not node):
                return f"node_id {new_id!r} existiert bereits."
            for e in self._wf.edges:
                if e.source_node_id == old_node_id:
                    e.source_node_id = new_id
                if e.target_node_id == old_node_id:
                    e.target_node_id = new_id
            node.node_id = new_id
        node.node_type = node_type.strip() or "noop"
        node.title = title.strip()
        node.description = description.strip()
        node.is_enabled = is_enabled
        node.config = dict(config)
        self.set_definition(self._wf)
        self._select_node_row(
            next(i for i, n in enumerate(self._wf.nodes) if n.node_id == new_id)
        )
        self.content_modified.emit()
        return None
