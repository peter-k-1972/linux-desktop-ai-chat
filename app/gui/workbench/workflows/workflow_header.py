"""
Shared header row for task-oriented canvases: title + primary/secondary actions.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.gui.shared.layout_constants import WIDGET_SPACING, apply_header_profile_margins
from app.gui.theme import design_metrics as dm


class WorkflowCanvasHeader(QFrame):
    """Actions are ``(label, callback)`` pairs; secondary styling via ``#secondaryButton`` in base QSS."""

    def __init__(
        self,
        title: str,
        subtitle: str | None,
        actions: list[tuple[str, Callable[[], None]]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workflowCanvasHeader")
        row = QHBoxLayout(self)
        apply_header_profile_margins(row, "compact")
        row.setSpacing(WIDGET_SPACING)
        titles = QVBoxLayout()
        titles.setSpacing(dm.SPACE_2XS_PX)
        tl = QLabel(title)
        tl.setObjectName("workbenchPanelHeaderTitle")
        titles.addWidget(tl)
        if subtitle:
            st = QLabel(subtitle)
            st.setObjectName("workbenchPanelHeaderSubtitle")
            st.setWordWrap(True)
            titles.addWidget(st)
        row.addLayout(titles, 1)
        for label, fn in actions:
            btn = QPushButton(label)
            btn.setObjectName("secondaryButton")
            btn.clicked.connect(fn)
            row.addWidget(btn)
