"""
Left dock: tree navigation for the Workbench.

Favorites / recent are persisted; context menus open objects as canvas tabs (same as activation).
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout, QWidget

from app.gui.workbench.explorer.explorer_items import ExplorerItemRef, ExplorerNodeKind
from app.gui.workbench.explorer.explorer_navigation_store import ExplorerNavigationStore
from app.gui.workbench.explorer.explorer_router import ExplorerRouter
from app.gui.workbench.explorer.explorer_tree_model import (
    create_explorer_tree_model,
    is_pinned_favorite,
    ref_from_index,
)
from app.gui.workbench.ui import EXPLORER_TREE_INDENT_PX, PanelHeader


class ExplorerPanel(QWidget):
    """``object`` payloads are :class:`ExplorerItemRef` for cross-thread-safe PySide typing."""

    explorer_item_activated = Signal(object)
    explorer_selection_changed = Signal(object)

    open_agent = Signal(str)
    open_workflow = Signal(str)
    open_file = Signal(str)
    open_chat_requested = Signal(str)

    def __init__(
        self,
        parent=None,
        *,
        project_names: Sequence[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchExplorerRoot")
        self._project_names = project_names
        self._store = ExplorerNavigationStore()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(
            PanelHeader(
                "Explorer",
                "Projects, library, runtime, and system. Opens items as canvas tabs.",
                parent=self,
            )
        )

        self._tree = QTreeView(self)
        self._tree.setObjectName("workbenchExplorerTree")
        self._tree.setHeaderHidden(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(EXPLORER_TREE_INDENT_PX)
        self._tree.setAlternatingRowColors(False)
        self._rebuild_model()
        layout.addWidget(self._tree, 1)
        ExplorerRouter(self._tree, self)

        sel = self._tree.selectionModel()
        sel.currentChanged.connect(self._on_current_changed)

        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

    def tree_view(self) -> QTreeView:
        return self._tree

    def _rebuild_model(self) -> None:
        fav = self._store.load_favorites()
        recent = self._store.load_recent()
        self._model = create_explorer_tree_model(
            self._project_names,
            favorites=fav,
            recent=recent,
        )
        self._tree.setModel(self._model)
        self._tree.expandToDepth(2)

    def record_activation(self, ref: ExplorerItemRef) -> None:
        """Call after a leaf opens a tab so Recent stays accurate."""
        if ref.kind == ExplorerNodeKind.FOLDER:
            return
        self._store.push_recent(ref)
        self._rebuild_model()

    def _on_current_changed(self, current, _previous) -> None:
        self.explorer_selection_changed.emit(ref_from_index(current))

    def _activate_ref(self, ref: ExplorerItemRef) -> None:
        self.explorer_item_activated.emit(ref)
        if ref.kind == ExplorerNodeKind.AGENT and ref.payload:
            self.open_agent.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.WORKFLOW and ref.payload:
            self.open_workflow.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.FILE and ref.payload:
            self.open_file.emit(ref.payload)
        elif ref.kind == ExplorerNodeKind.CHAT and ref.payload:
            self.open_chat_requested.emit(ref.payload)

    def _run_ref(self, ref: ExplorerItemRef) -> None:
        win = self.window()
        if hasattr(win, "console_panel"):
            win.console_panel.log_output(f"Run: {' / '.join(ref.path_labels)}")
        self._activate_ref(ref)

    def _duplicate_ref(self, ref: ExplorerItemRef) -> None:
        win = self.window()
        if not hasattr(win, "canvas_router"):
            return
        r = win.canvas_router
        if ref.kind == ExplorerNodeKind.WF_TEST_AGENT and ref.payload:
            r.open_agent_test(f"{ref.payload}-copy")
        elif ref.kind == ExplorerNodeKind.WF_KNOWLEDGE_BASE and ref.payload:
            r.open_knowledge_base_workflow(kb_id=f"{ref.payload}-copy", display_name=f"{ref.payload} copy")
        elif ref.kind == ExplorerNodeKind.WF_BUILD_WORKFLOW and ref.payload:
            r.open_workflow_builder(f"{ref.payload}-copy")
        elif ref.kind == ExplorerNodeKind.WF_PROMPT_DEV and ref.payload:
            r.open_prompt_development(f"{ref.payload}-copy")
        elif ref.kind == ExplorerNodeKind.WF_MODEL_COMPARE and ref.payload:
            r.open_model_compare(f"{ref.payload}-copy")
        elif ref.kind == ExplorerNodeKind.LIB_PROMPTS:
            r.open_prompt_development("copy")
        elif ref.kind == ExplorerNodeKind.LIB_MODELS:
            r.open_model_compare("copy")
        elif hasattr(win, "console_panel"):
            win.console_panel.log_output("Duplicate: not mapped for this item (stub).")

    def _export_ref(self, ref: ExplorerItemRef) -> None:
        win = self.window()
        if hasattr(win, "console_panel"):
            win.console_panel.log_output(f"Export (stub): {' / '.join(ref.path_labels)}")

    def _delete_ref(self, index, ref: ExplorerItemRef) -> None:
        if is_pinned_favorite(index):
            self._store.remove_favorite(ref)
            self._rebuild_model()
            return
        win = self.window()
        if hasattr(win, "console_panel"):
            win.console_panel.log_output("Delete is only wired for favorites in this build (stub).")

    def _on_context_menu(self, pos: QPoint) -> None:
        idx = self._tree.indexAt(pos)
        ref = ref_from_index(idx)
        menu = QMenu(self)

        if ref is not None and ref.kind != ExplorerNodeKind.FOLDER:
            open_act = QAction("Open", self)
            open_act.triggered.connect(lambda checked=False, r=ref: self._activate_ref(r))
            menu.addAction(open_act)
            run_act = QAction("Run", self)
            run_act.triggered.connect(lambda checked=False, r=ref: self._run_ref(r))
            menu.addAction(run_act)
            dup_act = QAction("Duplicate", self)
            dup_act.triggered.connect(lambda checked=False, r=ref: self._duplicate_ref(r))
            menu.addAction(dup_act)
            ex_act = QAction("Export…", self)
            ex_act.triggered.connect(lambda checked=False, r=ref: self._export_ref(r))
            menu.addAction(ex_act)
            menu.addSeparator()
            del_act = QAction("Delete", self)
            del_act.triggered.connect(lambda checked=False, i=idx, r=ref: self._delete_ref(i, r))
            menu.addAction(del_act)
            menu.addSeparator()

        fav_act = QAction("Add to favorites", self)
        fav_act.setEnabled(ref is not None and ref.kind != ExplorerNodeKind.FOLDER)
        if ref is not None:
            fav_act.triggered.connect(lambda checked=False, r=ref: self._add_favorite(r))
        menu.addAction(fav_act)

        rem_act = QAction("Remove from favorites", self)
        rem_act.setEnabled(ref is not None and is_pinned_favorite(idx))
        if ref is not None:
            rem_act.triggered.connect(lambda checked=False, r=ref: self._remove_favorite(r))
        menu.addAction(rem_act)

        menu.addSeparator()
        copy_act = QAction("Copy navigation path", self)
        copy_act.setEnabled(ref is not None)
        if ref is not None:
            copy_act.triggered.connect(lambda checked=False, r=ref: self._copy_path(r))
        menu.addAction(copy_act)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _add_favorite(self, ref: ExplorerItemRef) -> None:
        if ref.kind == ExplorerNodeKind.FOLDER:
            return
        self._store.add_favorite(ref)
        self._rebuild_model()

    def _remove_favorite(self, ref: ExplorerItemRef) -> None:
        self._store.remove_favorite(ref)
        self._rebuild_model()

    def _copy_path(self, ref: ExplorerItemRef) -> None:
        text = " / ".join(ref.path_labels)
        QGuiApplication.clipboard().setText(text)
