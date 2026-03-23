"""QGraphicsView mit Pan und leichtem Zoom."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class WorkflowGraphicsView(QGraphicsView):
    """Scrollbars = Pan; Strg+Mausrad = Zoom."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowGraphicsView")
        self.setRenderHints(
            self.renderHints()
            | QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._zoom = 1.0

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                factor = 1.12
            elif delta < 0:
                factor = 1 / 1.12
            else:
                return
            self._zoom = max(0.35, min(2.5, self._zoom * factor))
            self.resetTransform()
            self.scale(self._zoom, self._zoom)
            event.accept()
            return
        super().wheelEvent(event)

    def reset_zoom(self) -> None:
        self._zoom = 1.0
        self.resetTransform()
