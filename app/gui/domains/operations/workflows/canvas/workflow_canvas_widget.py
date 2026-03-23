"""Canvas mit Toolbar: Graph-Ansicht des aktuellen Workflows."""

from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.gui.domains.operations.workflows.canvas.workflow_scene import WorkflowGraphicsScene
from app.gui.domains.operations.workflows.canvas.workflow_view import WorkflowGraphicsView
from app.workflows.models.definition import WorkflowDefinition
from app.workflows.status import NodeRunStatus


class WorkflowCanvasWidget(QFrame):
    """Kapselt Szene + View; Signale nach außen für Editor/Workspace."""

    node_selected = Signal(object)
    definition_user_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowCanvasWidget")
        self._wf: Optional[WorkflowDefinition] = None
        self._scene = WorkflowGraphicsScene(self)
        self._scene.node_selected.connect(self.node_selected.emit)
        self._scene.definition_user_modified.connect(self.definition_user_modified.emit)

        self._view = WorkflowGraphicsView(self)
        self._view.setScene(self._scene)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        tb = QHBoxLayout()
        self._btn_connect = QPushButton("Kante ziehen (zwei Knoten anklicken)")
        self._btn_connect.setCheckable(True)
        self._btn_connect.toggled.connect(self._on_connect_toggled)
        self._btn_fit = QPushButton("Alles anzeigen")
        self._btn_fit.clicked.connect(self.fit_all)
        self._btn_zoom_reset = QPushButton("Zoom 100 %")
        self._btn_zoom_reset.clicked.connect(self._view.reset_zoom)
        tb.addWidget(self._btn_connect)
        tb.addWidget(self._btn_fit)
        tb.addWidget(self._btn_zoom_reset)
        tb.addWidget(QLabel("Pan: leerer Bereich ziehen · Zoom: Strg+Mausrad"))
        tb.addStretch()
        layout.addLayout(tb)
        layout.addWidget(self._view, 1)

    def _on_connect_toggled(self, on: bool) -> None:
        self._scene.set_connect_mode(on)
        self._btn_connect.setText(
            "Kante ziehen (aktiv – zwei Knoten wählen)" if on else "Kante ziehen (zwei Knoten anklicken)"
        )

    def set_definition(self, wf: Optional[WorkflowDefinition]) -> int:
        """
        Returns:
            Anzahl neu auto-platzierter Knoten in diesem Aufruf (für Workspace Dirty-Logik).
        """
        self._wf = wf
        n = self._scene.set_definition(wf)
        self._btn_connect.setChecked(False)
        self._scene.set_connect_mode(False)
        return n

    def reload_from_model(self) -> int:
        """Voller Rebuild aus derselben Definition-Referenz (nach Tabellenänderungen)."""
        return self._scene.set_definition(self._wf)

    def refresh_labels_only(self) -> None:
        self._scene.refresh_node_labels()

    def select_node_programmatic(self, node_id: Optional[str]) -> None:
        self._scene.select_node_programmatic(node_id)

    def set_node_run_status_overlay(self, mapping: Optional[Dict[str, Optional[NodeRunStatus]]]) -> None:
        self._scene.set_node_run_overlay(mapping)

    def fit_all(self) -> None:
        rect = self._scene.fit_nodes_rect()
        self._view.reset_zoom()
        self._view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
