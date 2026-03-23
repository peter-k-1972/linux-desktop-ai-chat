"""
Composite editor: node library + graphics view; exposed as a Workbench canvas tab.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.gui.workbench.ai_canvas.ai_canvas_scene import AiGraphScene
from app.gui.workbench.ai_canvas.ai_connection_model import AiGraphDocument
from app.gui.workbench.ai_canvas.ai_node_library_panel import AiNodeLibraryPanel
from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.ui import EmptyStateWidget, PanelHeader


class AiCanvasWidget(QWidget):
    """Embeddable graph surface; ``AiFlowEditorCanvas`` wraps this for the tab strip."""

    status_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._document = AiGraphDocument()
        self._scene = AiGraphScene(self._document, self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setObjectName("workbenchGraphView")
        self._view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self._view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self._library = AiNodeLibraryPanel(self)
        self._library.setMinimumWidth(200)
        self._library.setMaximumWidth(260)
        self._library.add_node_requested.connect(self._on_add_node)

        lib_wrap = QWidget(self)
        lib_lay = QVBoxLayout(lib_wrap)
        lib_lay.setContentsMargins(0, 0, 0, 0)
        lib_lay.setSpacing(0)
        lib_lay.addWidget(
            PanelHeader(
                "Node library",
                "Double-click a type to place it on the canvas.",
                parent=lib_wrap,
            )
        )
        lib_lay.addWidget(self._library, 1)

        self._empty_banner = EmptyStateWidget(
            "Start your graph",
            "Pick a node type on the left. Double-click adds the first block; drag blocks to arrange them.",
            "Edges and execution are wired in later phases — this view is spatial structure only.",
            parent=self,
        )
        self._empty_banner.setObjectName("workbenchAiEmptyBanner")

        view_wrap = QWidget(self)
        vw = QVBoxLayout(view_wrap)
        vw.setContentsMargins(0, 0, 0, 0)
        vw.setSpacing(8)
        vw.addWidget(self._empty_banner)
        vw.addWidget(self._view, 1)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setObjectName("workbenchAiSplitter")
        self._splitter.addWidget(lib_wrap)
        self._splitter.addWidget(view_wrap)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([220, 720])

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._splitter)

        self._sync_empty_banner()

    def update_status_display(self) -> None:
        self._emit_status()

    def graph_document(self) -> AiGraphDocument:
        return self._document

    def graphics_scene(self) -> AiGraphScene:
        return self._scene

    def selected_node_id(self) -> str | None:
        return self._scene.selected_node_id()

    def _on_add_node(self, type_id: str) -> None:
        offset = 40.0 + (len(self._document.nodes) % 8) * 24.0
        self._scene.add_node_of_type(type_id, x=offset, y=offset)
        self._sync_empty_banner()
        self._emit_status()

    def _sync_empty_banner(self) -> None:
        self._empty_banner.setVisible(len(self._document.nodes) == 0)

    def _emit_status(self) -> None:
        n = len(self._document.nodes)
        self.status_changed.emit(
            f"{n} node{'s' if n != 1 else ''} on canvas · Select a block to inspect properties"
        )


class AiFlowEditorCanvas(WorkbenchCanvasBase):
    """MVP AI graph editor tab; inspector reads ``graph_document`` and selection."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._body = AiCanvasWidget(self)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 0)
        outer.setSpacing(0)
        outer.addWidget(self._body, 1)

        strip = QFrame(self)
        strip.setObjectName("workbenchAiStatusStrip")
        s_lay = QHBoxLayout(strip)
        s_lay.setContentsMargins(12, 8, 12, 8)
        self._status = QLabel(self)
        self._status.setObjectName("workbenchAiStatusText")
        s_lay.addWidget(self._status)
        outer.addWidget(strip)

        self._body.status_changed.connect(self._status.setText)
        self._body.update_status_display()

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.AI_CANVAS

    @property
    def tab_key(self) -> str:
        return "ai-flow:main"

    @property
    def tab_title(self) -> str:
        return "AI Canvas"

    def graph_document(self) -> AiGraphDocument:
        return self._body.graph_document()

    def graphics_scene(self) -> AiGraphScene:
        return self._body.graphics_scene()

    def selected_node_id(self) -> str | None:
        return self._body.selected_node_id()
