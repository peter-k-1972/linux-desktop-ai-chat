"""
TopBar – App-weite Toolbar.

Enthält globale Aktionen (Status, Suche, etc.). Project Switcher für Projektkontext.
"""

from PySide6.QtWidgets import (
    QToolBar,
    QWidget,
    QSizePolicy,
    QLabel,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.project_switcher.project_switcher_button import ProjectSwitcherButton


class TopBar(QToolBar):
    """TopBar-Widget für die Hauptfenster-Toolbar."""

    command_palette_requested = Signal()
    status_requested = Signal()
    workspace_graph_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topBar")
        self.setMovable(False)
        self.setFloatable(False)

        self._project_switcher = ProjectSwitcherButton(self)
        self._add_content()
        self._connect_project_context()

    def _add_content(self):
        """Inhalt der TopBar."""
        app_title = QLabel("Linux Desktop Chat")
        app_title.setObjectName("topBarAppTitle")
        self.addWidget(app_title)

        self.addSeparator()

        self.addWidget(self._project_switcher)

        self.addSeparator()

        action_status = QAction(IconManager.get(IconRegistry.ACTIVITY, size=18), "Status", self)
        action_status.setToolTip("Runtime / Debug – Agent-Status, Aktivität")
        action_status.triggered.connect(self.status_requested.emit)
        self.addAction(action_status)

        action_graph = QAction(IconManager.get(IconRegistry.SYSTEM_GRAPH, size=18), "Workspace Map", self)
        action_graph.setToolTip("Workspace Graph – visual map of areas and workspaces")
        action_graph.triggered.connect(self.workspace_graph_requested.emit)
        self.addAction(action_graph)

        action_search = QAction(IconManager.get(IconRegistry.SEARCH, size=18), "Befehle", self)
        action_search.setToolTip("Command Palette – Befehle suchen (Ctrl+K)")
        action_search.triggered.connect(self.command_palette_requested.emit)
        self.addAction(action_search)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

    def _connect_project_context(self) -> None:
        """Project Switcher nutzt ProjectContextManager und project_context_changed."""
        # Der neue ProjectSwitcherButton aktualisiert sich selbst über project_context_changed.
        # Keine zusätzliche Verbindung nötig.
        pass
