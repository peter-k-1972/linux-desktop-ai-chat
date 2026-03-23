"""
Maps explorer tree activation to panel signals.

Selection changes are handled in :class:`ExplorerPanel`; this router only deals
with explicit item activation (click / keyboard).
"""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QObject
from PySide6.QtWidgets import QTreeView

from app.gui.workbench.explorer.explorer_items import ExplorerNodeKind
from app.gui.workbench.explorer.explorer_tree_model import ref_from_index


class ExplorerRouter(QObject):
    """Emits :pyattr:`ExplorerPanel.explorer_item_activated` for every resolved row."""

    def __init__(self, tree: QTreeView, panel: QObject) -> None:
        super().__init__(tree)
        self._tree = tree
        self._panel = panel
        tree.clicked.connect(self._on_clicked)
        tree.activated.connect(self._on_activated)

    def _resolve(self, index: QModelIndex) -> None:
        ref = ref_from_index(index)
        if ref is None:
            return
        self._panel.explorer_item_activated.emit(ref)
        # Narrow signals kept for programmatic / legacy hooks (same activation).
        if ref.kind == ExplorerNodeKind.AGENT and ref.payload:
            self._panel.open_agent.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.WORKFLOW and ref.payload:
            self._panel.open_workflow.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.FILE and ref.payload:
            self._panel.open_file.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.CHAT and ref.payload:
            self._panel.open_chat_requested.emit(ref.payload)

    def _on_clicked(self, index: QModelIndex) -> None:
        self._resolve(index)

    def _on_activated(self, index: QModelIndex) -> None:
        self._resolve(index)
