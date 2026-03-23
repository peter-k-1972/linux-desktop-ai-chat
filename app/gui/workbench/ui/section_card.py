"""
Framed inspector / settings block (Level 3 surface in the hierarchy).
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class SectionCard(QFrame):
    """Use ``body_layout()`` to add fields; styled as ``#workbenchSectionCard``."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchSectionCard")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 12)
        outer.setSpacing(8)
        tl = QLabel(title)
        tl.setObjectName("workbenchSectionCardTitle")
        outer.addWidget(tl)
        self._body = QVBoxLayout()
        self._body.setSpacing(8)
        outer.addLayout(self._body)

    def body_layout(self) -> QVBoxLayout:
        return self._body
