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
from app.gui.shared.layout_constants import CARD_SPACING, PANEL_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm


class ProjectOverviewPanel(QFrame):
    """Dashboard-Panel für Projekt-Details, Kennzahlen, Aktivität und Quick Actions."""

    set_active_requested = Signal(object)  # project dict
    edit_project_requested = Signal(object)
    delete_project_requested = Signal(object)
    manage_milestones_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectOverviewPanel")
        self._project = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        layout.setSpacing(CARD_SPACING)

        self._empty_label = QLabel("Projekt auswählen oder neues Projekt anlegen.")
        self._empty_label.setStyleSheet(
            f"color: #64748b; font-size: {dm.TEXT_LG_PX}px;"
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_label)

        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(CARD_SPACING)

        self._header_card = ProjectHeaderCard()
        content_layout.addWidget(self._header_card)

        self._stats_panel = ProjectStatsPanel()
        content_layout.addWidget(self._stats_panel)

        self._monitoring_frame = QFrame()
        self._monitoring_frame.setObjectName("projectMonitoringFrame")
        self._monitoring_frame.setStyleSheet(
            f"""
            #projectMonitoringFrame {{
                background: rgba(148, 163, 184, 0.06);
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: {dm.RADIUS_LG_PX}px;
                padding: {dm.CARD_PADDING_PX}px;
            }}
            """
        )
        mon_layout = QVBoxLayout(self._monitoring_frame)
        mon_layout.setSpacing(dm.SPACE_SM_PX)
        mon_title = QLabel("Betrieb / Monitoring")
        mon_title.setStyleSheet(
            f"font-weight: 600; font-size: {dm.TEXT_BASE_PX}px; color: #e2e8f0;"
        )
        mon_layout.addWidget(mon_title)
        self._mon_body = QLabel()
        self._mon_body.setWordWrap(True)
        self._mon_body.setStyleSheet(
            f"color: #94a3b8; font-size: {dm.TEXT_SM_PX}px; line-height: 1.45;"
        )
        mon_layout.addWidget(self._mon_body)
        content_layout.addWidget(self._monitoring_frame)

        self._controlling_frame = QFrame()
        self._controlling_frame.setObjectName("projectControllingFrame")
        self._controlling_frame.setStyleSheet(
            f"""
            #projectControllingFrame {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: {dm.RADIUS_LG_PX}px;
                padding: {dm.CARD_PADDING_PX}px;
            }}
            """
        )
        ctrl_layout = QVBoxLayout(self._controlling_frame)
        ctrl_layout.setSpacing(dm.SPACE_SM_PX)
        ctrl_title = QLabel("Planung & Controlling")
        ctrl_title.setStyleSheet(
            f"font-weight: 600; font-size: {dm.TEXT_BASE_PX}px; color: #e2e8f0;"
        )
        ctrl_layout.addWidget(ctrl_title)
        self._ctrl_budget = QLabel()
        self._ctrl_budget.setStyleSheet(
            f"color: #94a3b8; font-size: {dm.TEXT_SM_PX}px;"
        )
        self._ctrl_budget.hide()
        ctrl_layout.addWidget(self._ctrl_budget)
        self._ctrl_effort = QLabel()
        self._ctrl_effort.setStyleSheet(
            f"color: #94a3b8; font-size: {dm.TEXT_SM_PX}px;"
        )
        self._ctrl_effort.hide()
        ctrl_layout.addWidget(self._ctrl_effort)
        self._ctrl_next = QLabel()
        self._ctrl_next.setStyleSheet(
            f"color: #94a3b8; font-size: {dm.TEXT_SM_PX}px;"
        )
        ctrl_layout.addWidget(self._ctrl_next)
        self._ctrl_counts = QLabel()
        self._ctrl_counts.setStyleSheet(
            f"color: #94a3b8; font-size: {dm.TEXT_SM_PX}px;"
        )
        ctrl_layout.addWidget(self._ctrl_counts)
        self._ctrl_upcoming = QLabel()
        self._ctrl_upcoming.setWordWrap(True)
        self._ctrl_upcoming.setStyleSheet(
            f"color: #64748b; font-size: {dm.TEXT_XS_PX}px;"
        )
        self._ctrl_upcoming.hide()
        ctrl_layout.addWidget(self._ctrl_upcoming)
        self._btn_milestones = QPushButton("Meilensteine bearbeiten…")
        self._btn_milestones.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: {dm.RADIUS_MD_PX}px;
                padding: {dm.SPACE_SM_PX}px {dm.SPACE_LG_PX}px;
                color: #93c5fd;
            }}
            QPushButton:hover {{ background: rgba(59, 130, 246, 0.35); }}
            """
        )
        self._btn_milestones.clicked.connect(self._on_milestones_clicked)
        ctrl_layout.addWidget(self._btn_milestones)
        content_layout.addWidget(self._controlling_frame)

        self._actions_row = QHBoxLayout()
        self._actions_row.setSpacing(WIDGET_SPACING)
        self._btn_activate = QPushButton("Als aktives Projekt setzen")
        self._btn_activate.setIcon(IconManager.get(IconRegistry.RUN, size=16))
        self._btn_activate.setObjectName("activateProjectButton")
        self._btn_activate.setStyleSheet(f"""
            #activateProjectButton {{
                background: rgba(16, 185, 129, 0.3);
                border: 1px solid rgba(16, 185, 129, 0.5);
                border-radius: {dm.RADIUS_MD_PX}px;
                padding: {dm.SPACE_MD_PX}px {dm.SPACE_LG_PX}px;
                color: #6ee7b7;
                font-weight: 500;
            }}
            #activateProjectButton:hover {{
                background: rgba(16, 185, 129, 0.45);
            }}
        """)
        self._btn_activate.clicked.connect(self._on_set_active)
        self._actions_row.addWidget(self._btn_activate)

        self._btn_edit = QPushButton("Bearbeiten")
        self._btn_edit.setIcon(IconManager.get(IconRegistry.EDIT, size=16))
        self._btn_edit.setObjectName("editProjectButton")
        self._btn_edit.setStyleSheet(f"""
            #editProjectButton {{
                background: rgba(59, 130, 246, 0.25);
                border: 1px solid rgba(59, 130, 246, 0.45);
                border-radius: {dm.RADIUS_MD_PX}px;
                padding: {dm.SPACE_MD_PX}px {dm.SPACE_LG_PX}px;
                color: #93c5fd;
                font-weight: 500;
            }}
            #editProjectButton:hover {{ background: rgba(59, 130, 246, 0.4); }}
        """)
        self._btn_edit.clicked.connect(self._on_edit_clicked)
        self._actions_row.addWidget(self._btn_edit)

        self._btn_delete = QPushButton("Projekt löschen")
        self._btn_delete.setIcon(IconManager.get(IconRegistry.REMOVE, size=16))
        self._btn_delete.setObjectName("deleteProjectButton")
        self._btn_delete.setStyleSheet(f"""
            #deleteProjectButton {{
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.45);
                border-radius: {dm.RADIUS_MD_PX}px;
                padding: {dm.SPACE_MD_PX}px {dm.SPACE_LG_PX}px;
                color: #fca5a5;
                font-weight: 500;
            }}
            #deleteProjectButton:hover {{ background: rgba(239, 68, 68, 0.35); }}
        """)
        self._btn_delete.clicked.connect(self._on_delete_clicked)
        self._actions_row.addWidget(self._btn_delete)

        self._actions_row.addStretch()
        content_layout.addLayout(self._actions_row)

        middle_row = QHBoxLayout()
        middle_row.setSpacing(CARD_SPACING)
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
        self._quick_actions.open_workflows_requested.connect(self._on_quick_open_workflows)
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
            self._stats_panel.set_stats(0, 0, 0, 0)
            self._activity_panel.set_activity([], [], [])
            self._mon_body.setText("—")
            return

        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            self._stats_panel.set_stats(
                svc.count_workflows_of_project(pid),
                svc.count_chats_of_project(pid),
                svc.count_agents_of_project(pid),
                svc.count_files_of_project(pid),
            )
            self._sync_monitoring_section(pid, svc)
            activity = svc.get_recent_project_activity(pid, chat_limit=5, prompt_limit=5)
            self._activity_panel.set_activity(
                activity.get("recent_chats", []),
                activity.get("recent_prompts", []),
                activity.get("sources", []),
            )
            self._sync_controlling_section(pid, project, svc)
        except Exception:
            self._stats_panel.set_stats(0, 0, 0, 0)
            self._activity_panel.set_activity([], [], [])
            self._mon_body.setText("—")
            self._sync_controlling_section(pid, project, None)

    def _sync_monitoring_section(self, pid: int, svc) -> None:
        from app.projects.monitoring_display import monitoring_overview_lines

        if svc is None:
            self._mon_body.setText("—")
            return
        try:
            snap = svc.get_project_monitoring_snapshot(pid)
            self._mon_body.setText("\n".join(monitoring_overview_lines(snap)))
        except Exception:
            self._mon_body.setText("—")

    def _sync_controlling_section(self, pid: int, project: dict, svc) -> None:
        from app.projects.controlling import (
            format_budget_display,
            format_effort_display,
            format_milestone_compact_counts,
            format_next_milestone_line,
            milestone_summary,
        )

        if svc is None:
            try:
                from app.services.project_service import get_project_service

                svc = get_project_service()
            except Exception:
                self._ctrl_next.setText("Meilensteine: —")
                self._ctrl_counts.setText("")
                return

        btxt = format_budget_display(project.get("budget_amount"), project.get("budget_currency"))
        if btxt:
            self._ctrl_budget.setText(f"Budget: {btxt}")
            self._ctrl_budget.show()
        else:
            self._ctrl_budget.hide()

        etxt = format_effort_display(project.get("estimated_effort_hours"))
        if etxt:
            self._ctrl_effort.setText(f"Aufwandsschätzung: {etxt}")
            self._ctrl_effort.show()
        else:
            self._ctrl_effort.hide()

        try:
            ms = svc.list_project_milestones(pid)
            summary = milestone_summary(ms)
            nxt = format_next_milestone_line(summary.get("next_milestone"))
            self._ctrl_next.setText(f"Nächster Meilenstein: {nxt or '—'}")
            self._ctrl_counts.setText(
                format_milestone_compact_counts(
                    int(summary.get("open_count") or 0),
                    int(summary.get("overdue_count") or 0),
                )
            )
            up = summary.get("upcoming_three") or []
            if up:
                lines = []
                for m in up[:3]:
                    ln = format_next_milestone_line(m)
                    if ln:
                        lines.append(f"• {ln}")
                self._ctrl_upcoming.setText("Demnächst:\n" + "\n".join(lines))
                self._ctrl_upcoming.show()
            else:
                self._ctrl_upcoming.hide()
        except Exception:
            self._ctrl_next.setText("Nächster Meilenstein: —")
            self._ctrl_counts.setText("Offen: — · Überfällig: —")
            self._ctrl_upcoming.hide()

    def _on_milestones_clicked(self) -> None:
        if self._project:
            self.manage_milestones_requested.emit(self._project)

    def get_project(self) -> dict | None:
        """Liefert das aktuell angezeigte Projekt."""
        return self._project

    def _on_set_active(self) -> None:
        if self._project:
            self.set_active_requested.emit(self._project)

    def _on_edit_clicked(self) -> None:
        if self._project:
            self.edit_project_requested.emit(self._project)

    def _on_delete_clicked(self) -> None:
        if self._project:
            self.delete_project_requested.emit(self._project)

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
        """Gleicht das aktive Projekt mit der Overview-Auswahl ab (autoritativ: PCM)."""
        if not self._project:
            return
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            pid = self._project.get("project_id")
            if pid is None:
                return
            mgr = get_project_context_manager()
            if mgr.get_active_project_id() != pid:
                mgr.set_active_project(pid)
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

    def _on_quick_open_workflows(self) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context

            set_pending_context({"workflow_ops_scope": "project"})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea

            host.show_area(NavArea.OPERATIONS, "operations_workflows")
