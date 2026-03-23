"""
Scrollable list of registered node types; double-click adds a node to the graph.

Replaced later by drag-and-drop from the same catalog.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.gui.workbench.ai_canvas.ai_node_registry import all_node_types


class AiNodeLibraryPanel(QWidget):
    add_node_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._list = QListWidget(self)
        self._list.setObjectName("workbenchNodeLibrary")
        for meta in all_node_types():
            item = QListWidgetItem(f"{meta.group}: {meta.display_name}")
            item.setData(Qt.ItemDataRole.UserRole, meta.type_id)
            item.setToolTip(f"{meta.display_name} — double-click to place on canvas")
            self._list.addItem(item)
        self._list.itemDoubleClicked.connect(self._on_double)
        layout.addWidget(self._list)

    def _on_double(self, item: QListWidgetItem) -> None:
        tid = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(tid, str):
            self.add_node_requested.emit(tid)
