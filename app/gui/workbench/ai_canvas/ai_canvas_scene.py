"""
QGraphicsScene hosting movable node rectangles; edges stay in the document only (MVP).

Selection integrates with the Workbench inspector via :class:`AiFlowEditorCanvas`.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)

from app.gui.workbench.ai_canvas.ai_connection_model import AiGraphDocument
from app.gui.workbench.ai_canvas.ai_node_base import AiNodeInstance, new_node_id
from app.gui.workbench.ai_canvas.ai_node_registry import meta_for_type
from app.gui.themes import get_theme_manager
from app.gui.themes.canonical_token_ids import ThemeTokenId


class _NodeGraphicsItem(QGraphicsRectItem):
    def __init__(self, node_id: str, width: float = 150, height: float = 56) -> None:
        super().__init__(0, 0, width, height)
        self._node_id = node_id
        mgr = get_theme_manager()
        self.setPen(QPen(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_BORDER)), 1))
        self.setBrush(QBrush(QColor(mgr.color(ThemeTokenId.GRAPH_NODE_FILL))))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def node_id(self) -> str:
        return self._node_id

    def itemChange(self, change, value):  # noqa: ANN001
        result = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            sc = self.scene()
            if isinstance(sc, AiGraphScene):
                sc.sync_node_position(self._node_id)
        return result


class AiGraphScene(QGraphicsScene):
    def __init__(self, document: AiGraphDocument, parent=None) -> None:
        super().__init__(parent)
        self._document = document
        self._items: dict[str, _NodeGraphicsItem] = {}
        self.setSceneRect(QRectF(0, 0, 3200, 2400))

    def graph_document(self) -> AiGraphDocument:
        return self._document

    def add_node_of_type(self, type_id: str, *, x: float = 40, y: float = 40) -> str:
        meta = meta_for_type(type_id)
        title = meta.default_title if meta else type_id
        nid = new_node_id()
        node = AiNodeInstance(node_id=nid, type_id=type_id, title=title, x=x, y=y)
        self._document.nodes[nid] = node
        self._build_item(node)
        return nid

    def _build_item(self, node: AiNodeInstance) -> None:
        item = _NodeGraphicsItem(node.node_id)
        item.setPos(node.x, node.y)
        label = QGraphicsSimpleTextItem(node.title, item)
        label.setPos(8, 18)
        self.addItem(item)
        self._items[node.node_id] = item

    def sync_node_position(self, node_id: str) -> None:
        item = self._items.get(node_id)
        node = self._document.nodes.get(node_id)
        if item is None or node is None:
            return
        p = item.pos()
        node.x = float(p.x())
        node.y = float(p.y())

    def selected_node_id(self) -> str | None:
        for item in self.selectedItems():
            if isinstance(item, _NodeGraphicsItem):
                return item.node_id()
        return None
