"""
ProjectHubScreen – Screen wrapper for Project Hub.

Shows the ProjectHubPage (overview of active project).
"""

from PySide6.QtWidgets import QScrollArea, QFrame, QVBoxLayout
from PySide6.QtCore import Qt

from app.gui.shared import BaseScreen
from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.project_hub.project_hub_page import ProjectHubPage


class ProjectHubScreen(BaseScreen):
    """Project Hub – Overview of the active project."""

    def __init__(self, parent=None):
        super().__init__(NavArea.PROJECT_HUB, parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self._hub_page = ProjectHubPage(self)
        scroll.setWidget(self._hub_page)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
