"""
Right dock: context-sensitive inspector host with scroll and guided empty state.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.gui.workbench.focus.active_object import ActiveObject
from app.gui.workbench.ui import EmptyStateWidget, INSPECTOR_INNER_MARGIN_PX, PanelHeader, StatusChip


class InspectorPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchInspectorPanelRoot")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(
            PanelHeader(
                "Inspector",
                "Properties and context for the active canvas tab.",
                parent=self,
            )
        )

        self._focus_banner = QWidget(self)
        self._focus_banner.setObjectName("workbenchInspectorFocusBanner")
        fb_lay = QHBoxLayout(self._focus_banner)
        fb_lay.setContentsMargins(
            INSPECTOR_INNER_MARGIN_PX,
            8,
            INSPECTOR_INNER_MARGIN_PX,
            8,
        )
        self._focus_type_lbl = QLabel("", self._focus_banner)
        self._focus_type_lbl.setObjectName("workbenchInspectorFocusType")
        self._focus_chip = StatusChip("—", "Info", parent=self._focus_banner)
        fb_lay.addWidget(self._focus_type_lbl, 1)
        fb_lay.addWidget(self._focus_chip, 0, Qt.AlignmentFlag.AlignRight)
        outer.addWidget(self._focus_banner)

        self._scroll = QScrollArea(self)
        self._scroll.setObjectName("workbenchInspectorScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._inner = QWidget()
        self._inner.setObjectName("workbenchInspectorScrollInner")
        inner_lay = QVBoxLayout(self._inner)
        inner_lay.setContentsMargins(
            INSPECTOR_INNER_MARGIN_PX,
            INSPECTOR_INNER_MARGIN_PX,
            INSPECTOR_INNER_MARGIN_PX,
            INSPECTOR_INNER_MARGIN_PX,
        )
        inner_lay.setSpacing(0)

        self._content_host = QWidget(self._inner)
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

        self._empty_state = EmptyStateWidget(
            "Nothing selected",
            "Open a tab from the explorer or run a command from the palette.",
            "Tip: Ctrl+Shift+P opens the Command Palette.",
            parent=self._content_host,
        )
        self._content_layout.addWidget(self._empty_state, 1)

        inner_lay.addWidget(self._content_host, 1)
        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll, 1)

        self.set_focus_context(ActiveObject.none())

    def set_focus_context(self, active: ActiveObject) -> None:
        """Global active object banner (tab-driven); complements canvas-specific inspector body."""
        if active.is_empty():
            self._focus_banner.setVisible(False)
            return
        self._focus_banner.setVisible(True)
        oid = active.object_id or "—"
        self._focus_type_lbl.setText(f"{active.object_type.replace('_', ' ').title()} · {oid}")
        self._focus_chip.setText(active.status.value)

    def set_inspector(self, widget: QWidget | None) -> None:
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w is None:
                continue
            w.setParent(None)
            if w is not self._empty_state:
                w.deleteLater()

        if widget is None:
            self._empty_state.setParent(self._content_host)
            self._content_layout.addWidget(self._empty_state, 1)
        else:
            self._content_layout.addWidget(widget, 1)
