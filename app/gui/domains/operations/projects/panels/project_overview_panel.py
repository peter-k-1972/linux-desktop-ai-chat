"""
ProjectOverviewPanel – Projekt-Dashboard für den Project Overview Screen.

Projektkopf, Kennzahlen, Letzte Aktivität, Quick Actions.
Kein bloßer Begrüßungsscreen – ein Kontext-Hub für das aktive Projekt.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry

from app.gui.domains.operations.projects.panels.project_header_card import ProjectHeaderCard
from app.gui.domains.operations.projects.panels.project_stats_panel import ProjectStatsPanel
from app.gui.domains.operations.projects.panels.project_activity_panel import ProjectActivityPanel
from app.gui.domains.operations.projects.panels.project_quick_actions_panel import ProjectQuickActionsPanel


class ProjectOverviewPanel(QFrame):
    """Dashboard-Panel für Projekt-Details, Kennzahlen, Aktivität und Quick Actions."""

    set_active_requested = Signal(object)  # project dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectOverviewPanel")
        self._project = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self._empty_label = QLabel("Projekt auswählen oder neues Projekt anlegen.")
        self._empty_label.setStyleSheet("color: #64748b; font-size: 15px;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_label)

        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        self._header_card = ProjectHeaderCard()
        content_layout.addWidget(self._header_card)

        self._stats_panel = ProjectStatsPanel()
        content_layout.addWidget(self._stats_panel)

        self._actions_row = QHBoxLayout()
        self._actions_row.setSpacing(12)
        self._btn_activate = QPushButton("Als aktives Projekt setzen")
        self._btn_activate.setIcon(IconManager.get(IconRegistry.RUN, size=16))
        self._btn_activate.setObjectName("activateProjectButton")
        self._btn_activate.setStyleSheet("""
            #activateProjectButton {
                background: rgba(16, 185, 129, 0.3);
                border: 1px solid rgba(16, 185, 129, 0.5);
                border-radius: 8px;
                padding: 10px 18px;
                color: #6ee7b7;
                font-weight: 500;
            }
            #activateProjectButton:hover {
                background: rgba(16, 185, 129, 0.45);
            }
        """)
        self._btn_activate.clicked.connect(self._on_set_active)
        self._actions_row.addWidget(self._btn_activate)
        self._actions_row.addStretch()
        content_layout.addLayout(self._actions_row)

        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)
        self._activity_panel = ProjectActivityPanel()
        self._activity_panel.chat_clicked.connect(self._on_chat_clicked)
        self._activity_panel.prompt_clicked.connect(self._on_prompt_clicked)
        self._activity_panel.source_clicked.connect(self._on_source_clicked)
        middle_row.addWidget(self._activity_panel, 1)
        self._quick_actions = ProjectQuickActionsPanel()
        self._quick_actions.new_chat_requested.connect(self._on_quick_new_chat)
        self._quick_actions.add_source_requested.connect(self._on_quick_add_source)
        self._quick_actions.new_prompt_requested.connect(self._on_quick_new_prompt)
        self._quick_actions.open_knowledge_requested.connect(self._on_quick_open_knowledge)
        self._quick_actions.open_prompt_studio_requested.connect(self._on_quick_open_prompt_studio)
        self._quick_actions.open_agents_requested.connect(self._on_quick_open_agents)
        middle_row.addWidget(self._quick_actions)
        content_layout.addLayout(middle_row)

        self._content.hide()
        layout.addWidget(self._content, 1)

        self.setStyleSheet("""
            #projectOverviewPanel {
                background: transparent;
            }
        """)

    def set_project(self, project: dict | None) -> None:
        """Zeigt die Details eines Projekts."""
        self._project = project
        if not project:
            self._empty_label.show()
            self._content.hide()
            return
        self._empty_label.hide()
        self._content.show()

        self._header_card.set_project(project)
        pid = project.get("project_id")
        if not pid:
            self._stats_panel.set_stats(0, 0, 0)
            self._activity_panel.set_activity([], [], [])
            return

        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            self._stats_panel.set_stats(
                svc.count_chats_of_project(pid),
                len(svc.get_project_sources(pid)),
                svc.count_prompts_of_project(pid),
            )
            activity = svc.get_recent_project_activity(pid, chat_limit=5, prompt_limit=5)
            self._activity_panel.set_activity(
                activity.get("recent_chats", []),
                activity.get("recent_prompts", []),
                activity.get("sources", []),
            )
        except Exception:
            self._stats_panel.set_stats(0, 0, 0)
            self._activity_panel.set_activity([], [], [])

    def get_project(self) -> dict | None:
        """Liefert das aktuell angezeigte Projekt."""
        return self._project

    def _on_set_active(self) -> None:
        if self._project:
            self.set_active_requested.emit(self._project)

    def _find_workspace_host(self):
        """Findet den WorkspaceHost in der Parent-Hierarchie."""
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

    def _on_chat_clicked(self, chat_id: int) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"chat_id": chat_id})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_chat")

    def _on_prompt_clicked(self, prompt_id: int) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"prompt_id": prompt_id})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")

    def _on_source_clicked(self, source_path: str) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"source_path": source_path})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_knowledge")

    def _ensure_project_active(self) -> None:
        """Setzt das angezeigte Projekt als aktiv, falls noch nicht."""
        if not self._project:
            return
        try:
            from app.core.context.active_project import get_active_project_context
            ctx = get_active_project_context()
            if ctx.active_project_id != self._project.get("project_id"):
                ctx.set_active(project=self._project)
        except Exception:
            pass

    def _on_quick_new_chat(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_chat")

    def _on_quick_add_source(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_knowledge")

    def _on_quick_new_prompt(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")

    def _on_quick_open_knowledge(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_knowledge")

    def _on_quick_open_prompt_studio(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")

    def _on_quick_open_agents(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_agent_tasks")
