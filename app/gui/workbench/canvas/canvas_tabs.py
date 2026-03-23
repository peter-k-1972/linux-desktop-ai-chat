"""
Central tab strip (QTabWidget) for Workbench canvases.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QStyle, QTabWidget

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.focus.object_status import ObjectStatus
from app.gui.themes.canonical_token_ids import ThemeTokenId


def _kind_standard_pixmap(kind: CanvasKind) -> QStyle.StandardPixmap:
    if kind in (CanvasKind.AGENT, CanvasKind.WF_AGENT_TEST):
        return QStyle.StandardPixmap.SP_ComputerIcon
    if kind in (CanvasKind.WORKFLOW, CanvasKind.WF_WORKFLOW_BUILDER, CanvasKind.AI_CANVAS):
        return QStyle.StandardPixmap.SP_FileDialogDetailedView
    if kind == CanvasKind.WF_KNOWLEDGE_BASE:
        return QStyle.StandardPixmap.SP_DirIcon
    if kind == CanvasKind.WF_PROMPT_DEV:
        return QStyle.StandardPixmap.SP_FileDialogInfoView
    if kind == CanvasKind.WF_MODEL_COMPARE:
        return QStyle.StandardPixmap.SP_ArrowRight
    if kind == CanvasKind.CHAT:
        return QStyle.StandardPixmap.SP_MessageBoxInformation
    if kind == CanvasKind.FILE:
        return QStyle.StandardPixmap.SP_FileIcon
    if kind == CanvasKind.FEATURE:
        return QStyle.StandardPixmap.SP_TitleBarNormalButton
    return QStyle.StandardPixmap.SP_FileDialogContentsView


def _status_color(status: ObjectStatus) -> QColor:
    from app.gui.themes import get_theme_manager

    mgr = get_theme_manager()
    tok = {
        ObjectStatus.READY: ThemeTokenId.INDICATOR_READY,
        ObjectStatus.RUNNING: ThemeTokenId.INDICATOR_RUNNING,
        ObjectStatus.FAILED: ThemeTokenId.INDICATOR_FAILED,
        ObjectStatus.INDEXING: ThemeTokenId.INDICATOR_INDEXING,
        ObjectStatus.SYNCING: ThemeTokenId.INDICATOR_SYNCING,
    }[status]
    return QColor(mgr.color(tok))


def _compose_tab_icon(base: QIcon, status: ObjectStatus, device_pixel_ratio: float = 1.0) -> QIcon:
    size = 20
    pm = QPixmap(int(size * device_pixel_ratio), int(size * device_pixel_ratio))
    pm.setDevicePixelRatio(device_pixel_ratio)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    base.paint(painter, 0, 0, size, size)
    dot = _status_color(status)
    painter.setBrush(dot)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(size - 7, size - 7, 6, 6)
    painter.end()
    return QIcon(pm)


class CanvasTabs(QTabWidget):
    """Closable tabs; deduplicates by ``WorkbenchCanvasBase.tab_key``."""

    tab_canvas_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchCanvasTabs")
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self._status_by_key: dict[str, ObjectStatus] = {}
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.currentChanged.connect(self._emit_active_canvas)

    def current_canvas(self) -> WorkbenchCanvasBase | None:
        w = self.currentWidget()
        return w if isinstance(w, WorkbenchCanvasBase) else None

    def find_tab_index_by_key(self, tab_key: str) -> int:
        for i in range(self.count()):
            w = self.widget(i)
            if isinstance(w, WorkbenchCanvasBase) and w.tab_key == tab_key:
                return i
        return -1

    def tab_status(self, tab_key: str) -> ObjectStatus:
        return self._status_by_key.get(tab_key, ObjectStatus.READY)

    def set_tab_status(self, tab_key: str, status: ObjectStatus) -> None:
        self._status_by_key[tab_key] = status
        idx = self.find_tab_index_by_key(tab_key)
        if idx >= 0:
            self._apply_tab_chrome(idx)

    def open_canvas(self, canvas: WorkbenchCanvasBase) -> None:
        idx = self.find_tab_index_by_key(canvas.tab_key)
        if idx >= 0:
            self.setCurrentIndex(idx)
            self._apply_tab_chrome(idx)
            return
        if canvas.tab_key not in self._status_by_key:
            self._status_by_key[canvas.tab_key] = ObjectStatus.READY
        self.addTab(canvas, canvas.tab_title)
        new_idx = self.count() - 1
        self._apply_tab_chrome(new_idx)
        self.setCurrentIndex(new_idx)

    def _on_tab_close_requested(self, index: int) -> None:
        w = self.widget(index)
        if isinstance(w, WorkbenchCanvasBase):
            self._status_by_key.pop(w.tab_key, None)
        self.removeTab(index)
        self._emit_active_canvas(self.currentIndex())

    def _apply_tab_chrome(self, index: int) -> None:
        w = self.widget(index)
        if not isinstance(w, WorkbenchCanvasBase):
            return
        style = QApplication.style()
        if style is None:
            return
        base_ico = style.standardIcon(_kind_standard_pixmap(w.canvas_kind))
        st = self._status_by_key.get(w.tab_key, ObjectStatus.READY)
        dpr = self.devicePixelRatioF()
        self.setTabIcon(index, _compose_tab_icon(base_ico, st, dpr))
        self.setTabToolTip(index, f"{w.tab_title}\nStatus: {st.value}")

    def _emit_active_canvas(self, index: int) -> None:
        if index < 0:
            self.tab_canvas_changed.emit(None)
            return
        w = self.widget(index)
        self.tab_canvas_changed.emit(w if isinstance(w, WorkbenchCanvasBase) else None)
