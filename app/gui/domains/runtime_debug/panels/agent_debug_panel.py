"""
Agent Debug Panel – Hauptpanel für Agenten-Debug-Ansicht.

Bündelt alle Debug-Views (Activity, Timeline, Model Usage, Tool Execution, Task Graph)
und bietet einblendbar/deaktivierbar Optionen.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QCheckBox,
)
from PySide6.QtCore import Qt, Signal, QTimer

from app.debug.debug_store import DebugStore, get_debug_store
from app.gui.domains.runtime_debug.panels.agent_activity_view import AgentActivityView
from app.gui.domains.runtime_debug.panels.event_timeline_view import EventTimelineView
from app.gui.domains.runtime_debug.panels.model_usage_view import ModelUsageView
from app.gui.domains.runtime_debug.panels.tool_execution_view import ToolExecutionView
from app.gui.domains.runtime_debug.panels.task_graph_view import TaskGraphView


class AgentDebugPanel(QWidget):
    """
    Debug-Panel für Agenten-Aktivität.

    - Einblendbar via Toggle
    - Optional deaktivierbar (keine Events wenn deaktiviert)
    - Aktualisiert sich periodisch aus dem DebugStore
    """

    visibility_changed = Signal(bool)  # True wenn sichtbar

    def __init__(
        self,
        store: DebugStore | None = None,
        theme: str = "dark",
        enabled: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self._store = store or get_debug_store()
        self._theme = theme
        self._enabled = enabled
        self._init_ui()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_all)
        self._refresh_timer.start(500)  # Alle 500ms aktualisieren

    def _init_ui(self):
        self.setObjectName("agentDebugPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header mit Clear-Button
        header = QHBoxLayout()
        title = QLabel("Agent Debug")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(title)
        header.addStretch()
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setToolTip("Debug-Daten löschen")
        self._clear_btn.clicked.connect(self._on_clear)
        header.addWidget(self._clear_btn)
        layout.addLayout(header)

        self._tabs = QTabWidget()
        self._activity_view = AgentActivityView(self._store, self._theme)
        self._tabs.addTab(self._activity_view, "Aktivität")

        self._timeline_view = EventTimelineView(self._store, self._theme)
        self._tabs.addTab(self._timeline_view, "Timeline")

        self._task_graph_view = TaskGraphView(self._store, self._theme)
        self._tabs.addTab(self._task_graph_view, "Task-Graph")

        self._model_view = ModelUsageView(self._store, self._theme)
        self._tabs.addTab(self._model_view, "Modelle")

        self._tool_view = ToolExecutionView(self._store, self._theme)
        self._tabs.addTab(self._tool_view, "Tools")

        layout.addWidget(self._tabs)

    def _refresh_all(self):
        """Aktualisiert alle Views."""
        if not self._enabled or not self.isVisible():
            return
        self._activity_view.refresh()
        self._timeline_view.refresh()
        self._task_graph_view.refresh()
        self._model_view.refresh()
        self._tool_view.refresh()

    def _on_clear(self):
        """Löscht alle Debug-Daten."""
        self._store.clear()
        self._refresh_all()

    def set_theme(self, theme: str):
        """Setzt das Theme für alle Child-Views."""
        self._theme = theme
        self._activity_view.set_theme(theme)
        self._timeline_view.set_theme(theme)
        self._task_graph_view.set_theme(theme)
        self._model_view.set_theme(theme)
        self._tool_view.set_theme(theme)

    def set_enabled(self, enabled: bool):
        """Aktiviert oder deaktiviert das Debug-Panel (Performance)."""
        self._enabled = enabled

    def is_debug_enabled(self) -> bool:
        """Liefert ob das Debug-Panel aktiv ist."""
        return self._enabled
