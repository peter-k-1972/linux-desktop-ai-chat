"""Darstellung eines Workflow-Knotens (nur Grafik + Interaktion)."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QStyleOptionGraphicsItem, QWidget

from app.workflows.status import NodeRunStatus

from app.gui.themes.canonical_token_ids import ThemeTokenId


class WorkflowNodeItem(QGraphicsObject):
    """Rechteck mit Text; referenziert nur node_id fürs Modell."""

    position_committed = Signal(str, float, float)
    connect_pick_requested = Signal(str)

    NODE_W = 168.0
    NODE_H = 80.0

    def __init__(self, node_id: str, title: str, node_type: str, parent=None):
        super().__init__(parent)
        self._node_id = node_id
        self._title = (title or node_id)[:48]
        self._type = (node_type or "")[:24]
        self._run_status: Optional[NodeRunStatus] = None
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        res = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            sc = self.scene()
            if sc is not None and hasattr(sc, "update_incident_edges"):
                sc.update_incident_edges(self._node_id)
        return res

    @property
    def node_id(self) -> str:
        return self._node_id

    def set_labels(self, title: str, node_type: str) -> None:
        self._title = (title or self._node_id)[:48]
        self._type = (node_type or "")[:24]
        self.update()

    def set_run_status_overlay(self, status: Optional[NodeRunStatus]) -> None:
        """Read-only Run-Hinweis aus NodeRun; None = neutral (kein Eintrag im gewählten Run)."""
        self._run_status = status
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.NODE_W, self.NODE_H)

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        from app.gui.themes import get_theme_manager

        mgr = get_theme_manager()
        r = self.boundingRect()
        fill, border = _run_overlay_colors(self._run_status)
        pen = QPen(border, 1.5)
        if option.state & QStyleOptionGraphicsItem.StateFlag.State_Selected:
            pen = QPen(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_SELECTED_BORDER)), 2.5)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(r, 6, 6)
        painter.setPen(QPen(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_TEXT))))
        f = QFont()
        f.setPointSize(10)
        f.setBold(True)
        painter.setFont(f)
        painter.drawText(r.adjusted(8, 8, -8, -36), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
        f.setBold(False)
        f.setPointSize(9)
        painter.setFont(f)
        painter.setPen(QPen(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_TEXT_MUTED))))
        painter.drawText(r.adjusted(8, 32, -8, -22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._type)
        painter.setPen(QPen(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_TEXT_MUTED))))
        f.setPointSize(8)
        painter.setFont(f)
        painter.drawText(r.adjusted(8, 58, -8, -6), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._node_id)

    def mousePressEvent(self, event) -> None:
        scene = self.scene()
        if (
            scene is not None
            and getattr(scene, "connect_mode", False)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.connect_pick_requested.emit(self._node_id)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not getattr(
            self.scene(), "connect_mode", False
        ):
            p = self.pos()
            self.position_committed.emit(self._node_id, p.x(), p.y())

    def center_scene_pos(self) -> QPointF:
        return self.scenePos() + QPointF(self.NODE_W / 2, self.NODE_H / 2)

    def anchor_out(self) -> QPointF:
        """Rechte Mitte für Kanten."""
        return self.scenePos() + QPointF(self.NODE_W, self.NODE_H / 2)

    def anchor_in(self) -> QPointF:
        """Linke Mitte für Kanten."""
        return self.scenePos() + QPointF(0, self.NODE_H / 2)


def _run_overlay_colors(status: Optional[NodeRunStatus]) -> tuple[QColor, QColor]:
    """(Füllfarbe, Randfarbe) aus Theme-Tokens (THEME_TOKEN_SPEC — Graph)."""
    from app.gui.themes import get_theme_manager

    m = get_theme_manager()
    if status is None:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_FILL)), QColor(m.color(ThemeTokenId.GRAPH_NODE_BORDER))
    if status == NodeRunStatus.COMPLETED:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_STATUS_COMPLETED_FILL)), QColor(
            m.color(ThemeTokenId.GRAPH_NODE_STATUS_COMPLETED_BORDER)
        )
    if status == NodeRunStatus.FAILED:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_STATUS_FAILED_FILL)), QColor(
            m.color(ThemeTokenId.GRAPH_NODE_STATUS_FAILED_BORDER)
        )
    if status == NodeRunStatus.RUNNING:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_STATUS_RUNNING_FILL)), QColor(
            m.color(ThemeTokenId.GRAPH_NODE_STATUS_RUNNING_BORDER)
        )
    if status == NodeRunStatus.PENDING:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_STATUS_PENDING_FILL)), QColor(
            m.color(ThemeTokenId.GRAPH_NODE_STATUS_PENDING_BORDER)
        )
    if status == NodeRunStatus.CANCELLED:
        return QColor(m.color(ThemeTokenId.GRAPH_NODE_STATUS_CANCELLED_FILL)), QColor(
            m.color(ThemeTokenId.GRAPH_NODE_STATUS_CANCELLED_BORDER)
        )
    return QColor(m.color(ThemeTokenId.GRAPH_NODE_FILL)), QColor(m.color(ThemeTokenId.GRAPH_NODE_BORDER))
