"""
Consistent panel title + optional subtitle for Explorer, Inspector, Console, etc.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.gui.shared.layout_constants import apply_header_profile_margins
from app.gui.theme import design_metrics as dm


class PanelHeader(QWidget):
    """Styled via ``#workbenchPanelHeader`` / title / subtitle IDs in ``workbench.qss``."""

    def __init__(self, title: str, subtitle: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchPanelHeader")
        lay = QVBoxLayout(self)
        apply_header_profile_margins(lay, "standard")
        lay.setSpacing(dm.SPACE_2XS_PX)
        t = QLabel(title)
        t.setObjectName("workbenchPanelHeaderTitle")
        lay.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("workbenchPanelHeaderSubtitle")
            s.setWordWrap(True)
            lay.addWidget(s)
