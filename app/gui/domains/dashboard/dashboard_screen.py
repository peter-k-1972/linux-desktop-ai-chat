"""
DashboardScreen – Kommandozentrale.

System Status, Active Work, QA Status, Incidents (Live- bzw. QA-JSON-Refresh).
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QGridLayout,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShowEvent
from app.gui.shared import BaseScreen
from app.gui.domains.dashboard.panels import (
    SystemStatusPanel,
    ActiveWorkPanel,
    QAStatusPanel,
    IncidentsPanel,
)
from app.gui.navigation.nav_areas import NavArea


class DashboardScreen(BaseScreen):
    """Kommandozentrale – Dashboard mit Status-Karten."""

    def __init__(self, parent=None):
        super().__init__(NavArea.COMMAND_CENTER, parent)
        self._system_panel: SystemStatusPanel | None = None
        self._qa_panel: QAStatusPanel | None = None
        self._incidents_panel: IncidentsPanel | None = None
        self._setup_ui()
        QTimer.singleShot(0, self._refresh_dynamic_panels)

    def _refresh_dynamic_panels(self) -> None:
        for p in (self._system_panel, self._qa_panel, self._incidents_panel):
            if p is not None and hasattr(p, "refresh"):
                p.refresh()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Kommandozentrale")
        title.setObjectName("primaryTitle")
        layout.addWidget(title)

        hint = QLabel(
            "Überblick aus lokaler Laufzeit und docs/qa-Artefakten. "
            "Vertiefung: gleiche Navigationsarea → Command Center (Karten & Drilldowns)."
        )
        hint.setWordWrap(True)
        hint.setObjectName("panelMeta")
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setSpacing(20)

        self._system_panel = SystemStatusPanel()
        self._qa_panel = QAStatusPanel()
        self._incidents_panel = IncidentsPanel()
        grid.addWidget(self._system_panel, 0, 0)
        grid.addWidget(ActiveWorkPanel(), 0, 1)
        grid.addWidget(self._qa_panel, 1, 0)
        grid.addWidget(self._incidents_panel, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._refresh_dynamic_panels()
