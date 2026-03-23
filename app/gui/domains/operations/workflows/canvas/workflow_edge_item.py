"""Kante als Linie zwischen zwei Knoten-Items."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

from app.gui.themes.canonical_token_ids import ThemeTokenId
from PySide6.QtWidgets import QGraphicsLineItem, QMenu

if TYPE_CHECKING:
    from app.gui.domains.operations.workflows.canvas.workflow_node_item import WorkflowNodeItem


class WorkflowEdgeItem(QGraphicsLineItem):
    """Linie source -> target; löschbar per Kontextmenü.

    Kein Qt-Signal auf dem Item: QGraphicsLineItem erbt kein QObject — Callback von der Szene.
    """

    def __init__(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        on_delete_requested: Callable[[str], None],
    ):
        super().__init__()
        self._edge_id = edge_id
        self._source_id = source_id
        self._target_id = target_id
        self._on_delete_requested = on_delete_requested
        from app.gui.themes import get_theme_manager

        edge = get_theme_manager().color(ThemeTokenId.GRAPH_EDGE)
        self.setPen(QPen(QColor(edge), 1.8))
        self.setZValue(-2)
        self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

    @property
    def edge_id(self) -> str:
        return self._edge_id

    def update_geometry(
        self,
        src: Optional[WorkflowNodeItem],
        tgt: Optional[WorkflowNodeItem],
    ) -> None:
        if src is None or tgt is None:
            self.setLine(0, 0, 0, 0)
            return
        p0 = src.anchor_out()
        p1 = tgt.anchor_in()
        self.setLine(p0.x(), p0.y(), p1.x(), p1.y())

    def contextMenuEvent(self, event) -> None:
        menu = QMenu()
        act = menu.addAction("Kante löschen")
        act.triggered.connect(lambda: self._on_delete_requested(self._edge_id))
        menu.exec(event.screenPos())
        event.accept()
