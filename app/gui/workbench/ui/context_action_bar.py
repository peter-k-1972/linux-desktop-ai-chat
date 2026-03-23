"""
Contextual actions above the canvas (IDE-style); content follows :class:`ActiveObject`.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from app.gui.shared.layout_constants import apply_header_profile_margins
from app.gui.theme import design_metrics as dm
from app.gui.workbench.focus.active_object import ActiveObject
from app.gui.workbench.focus.contextual_actions import contextual_action_tuples
from app.gui.workbench.focus.object_status import ObjectStatus


def _status_label_text(status: ObjectStatus) -> str:
    return f"Status · {status.value}"


class ContextActionBar(QWidget):
    def __init__(self, window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchContextActionBar")
        self._window = window
        self._layout = QHBoxLayout(self)
        apply_header_profile_margins(self._layout, "ultra")
        self._layout.setSpacing(dm.SPACE_SM_PX)

        self._object_lbl = QLabel("", self)
        self._object_lbl.setObjectName("workbenchContextObjectLabel")
        self._object_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._status_lbl = QLabel("", self)
        self._status_lbl.setObjectName("workbenchContextStatusLabel")
        self._status_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._layout.addWidget(self._object_lbl)
        self._layout.addWidget(self._status_lbl)
        self._layout.addStretch(1)

        self._buttons: list[QPushButton] = []
        self.sync_from_focus(window.focus_controller.active_object)

    def sync_from_focus(self, active: ActiveObject) -> None:
        for b in self._buttons:
            self._layout.removeWidget(b)
            b.deleteLater()
        self._buttons.clear()

        if active.is_empty():
            self._object_lbl.setText("No active object — open a tab from the explorer or palette.")
            self._status_lbl.setText("")
            return

        oid = active.object_id or "—"
        self._object_lbl.setText(f"{active.object_type.replace('_', ' ').title()} · {oid}")
        self._status_lbl.setText(_status_label_text(active.status))

        for label, fn in contextual_action_tuples(self._window, active):
            btn = QPushButton(label, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(fn)
            self._layout.addWidget(btn)
            self._buttons.append(btn)
