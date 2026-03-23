"""
Guided empty / placeholder content (what this area is + what to do next).
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyStateWidget(QWidget):
    """Three-line pattern: title, explanation, concrete next step."""

    def __init__(
        self,
        title: str,
        body: str,
        hint: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchEmptyState")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 28, 24, 28)
        lay.setSpacing(10)
        t = QLabel(title)
        t.setObjectName("workbenchEmptyStateTitle")
        t.setWordWrap(True)
        lay.addWidget(t)
        b = QLabel(body)
        b.setObjectName("workbenchEmptyStateBody")
        b.setWordWrap(True)
        lay.addWidget(b)
        if hint:
            h = QLabel(hint)
            h.setObjectName("workbenchEmptyStateHint")
            h.setWordWrap(True)
            lay.addWidget(h)
        lay.addStretch(1)
