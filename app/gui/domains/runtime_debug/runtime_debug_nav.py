"""
RuntimeDebugNav – Sekundäre Navigation innerhalb von Runtime / Debug.

Bereichsleiste: EventBus, Logs, Metrics, LLM Calls, Agent Activity, System Graph.
Technisch, Monitoring-Charakter.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QFrame
from PySide6.QtCore import Signal, Qt
from app.gui.icons import IconManager
from app.gui.icons.nav_mapping import RD_WORKSPACE_ICONS


class RuntimeDebugNav(QFrame):
    """Sub-Navigation für Runtime-/Debug-Bereiche."""

    workspace_selected = Signal(str)

    _WORKSPACES_BASE = [
        ("rd_introspection", "Introspection"),
        ("rd_qa_cockpit", "QA Cockpit"),
        ("rd_qa_observability", "QA Observability"),
        ("rd_markdown_demo", "Markdown Demo"),
        ("rd_eventbus", "EventBus"),
        ("rd_logs", "Logs"),
        ("rd_metrics", "Metrics"),
        ("rd_llm_calls", "LLM Calls"),
        ("rd_agent_activity", "Agent Activity"),
        ("rd_system_graph", "System Graph"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("runtimeDebugNav")
        self.setMinimumWidth(180)
        self.setMaximumWidth(220)
        self._workspaces = self._build_workspace_list()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(4)

        title = QLabel("Runtime / Debug")
        title.setObjectName("runtimeNavTitle")
        layout.addWidget(title)

        subtitle = QLabel("Systemzustände · Events · Metriken")
        subtitle.setObjectName("runtimeNavSubtitle")
        layout.addWidget(subtitle)

        self._list = QListWidget()
        self._list.setObjectName("runtimeDebugNavList")
        self._list.setSpacing(4)
        self._list.itemClicked.connect(self._on_item_clicked)

        for area_id, title in self._workspaces:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, area_id)
            icon_name = RD_WORKSPACE_ICONS.get(area_id)
            if icon_name:
                item.setIcon(IconManager.get(icon_name, size=18, color_token="color_monitoring_text"))
            self._list.addItem(item)

        layout.addWidget(self._list, 1)

    @staticmethod
    def _build_workspace_list() -> list[tuple[str, str]]:
        """
        Gleiche erlaubte Nav-Menge wie Sidebar (FeatureRegistry); Theme Visualizer
        nur wenn DevTools aktiv und ``nav.rd_theme_visualizer`` in den aktiven Kommandos.
        """
        from app.features import collect_active_gui_command_ids, get_feature_registry
        from app.gui.devtools.devtools_visibility import is_theme_visualizer_available
        from app.gui.navigation.nav_context import allowed_navigation_entry_ids

        allowed = allowed_navigation_entry_ids()
        out = [
            (a, t)
            for a, t in RuntimeDebugNav._WORKSPACES_BASE
            if allowed is None or a in allowed
        ]
        if is_theme_visualizer_available():
            fr = get_feature_registry()
            cmds = collect_active_gui_command_ids(fr) if fr is not None else None
            if cmds is None or "nav.rd_theme_visualizer" in cmds:
                out.append(("rd_theme_visualizer", "Theme Visualizer"))
        return out

    def _on_item_clicked(self, item: QListWidgetItem):
        area_id = item.data(Qt.ItemDataRole.UserRole)
        if area_id:
            self.workspace_selected.emit(area_id)

    def set_current(self, area_id: str) -> None:
        """Setzt den aktuell ausgewählten Eintrag."""
        for i in range(self._list.count()):
            if self._list.item(i).data(Qt.ItemDataRole.UserRole) == area_id:
                self._list.setCurrentRow(i)
                break
