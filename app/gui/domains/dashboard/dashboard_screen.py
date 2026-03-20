"""
DashboardScreen – Kommandozentrale.

Enthält System Status, Active Work, QA Status, Incidents.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QGridLayout,
    QLabel,
)
from PySide6.QtCore import Qt
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
        self._setup_ui()

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

        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(SystemStatusPanel(), 0, 0)
        grid.addWidget(ActiveWorkPanel(), 0, 1)
        grid.addWidget(QAStatusPanel(), 1, 0)
        grid.addWidget(IncidentsPanel(), 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
