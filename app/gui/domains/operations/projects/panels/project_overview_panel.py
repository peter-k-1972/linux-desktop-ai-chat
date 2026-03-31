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
from app.gui.domains.operations.projects.project_overview_sink import ProjectOverviewSink
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry

from app.gui.domains.operations.projects.panels.project_header_card import ProjectHeaderCard
from app.gui.domains.operations.projects.panels.project_stats_panel import ProjectStatsPanel
from app.gui.domains.operations.projects.panels.project_activity_panel import ProjectActivityPanel
from app.gui.domains.operations.projects.panels.project_quick_actions_panel import ProjectQuickActionsPanel
from app.gui.shared.layout_constants import CARD_SPACING, PANEL_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm
from app.ui_application.adapters.service_projects_overview_command_adapter import (
    ServiceProjectsOverviewCommandAdapter,
)
from app.ui_application.adapters.service_projects_overview_read_adapter import (
    ServiceProjectsOverviewReadAdapter,
)
from app.ui_application.presenters.project_overview_presenter import ProjectOverviewPresenter
from app.ui_application.ports.projects_overview_command_port import ProjectsOverviewCommandPort
from app.ui_application.ports.projects_overview_host_callbacks import ProjectsOverviewHostCallbacks
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import ProjectOverviewState


class ProjectOverviewPanel(QFrame):
    """Dashboard-Panel für Projekt-Details, Kennzahlen, Aktivität und Quick Actions."""

    set_active_requested = Signal(object)  # project dict
    edit_project_requested = Signal(object)
    delete_project_requested = Signal(object)
    manage_milestones_requested = Signal(object)

    def __init__(
        self,
        parent=None,
        *,
        read_port: ProjectsOverviewReadPort | None = None,
        command_port: ProjectsOverviewCommandPort | None = None,
        host_callbacks: ProjectsOverviewHostCallbacks | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("projectOverviewPanel")
        self._project = None
        self._setup_ui()
        self._sink = ProjectOverviewSink(self)
        self._presenter = ProjectOverviewPresenter(
            sink=self._sink,
            read_port=read_port or ServiceProjectsOverviewReadAdapter(),
            command_port=command_port or ServiceProjectsOverviewCommandAdapter(),
            host_callbacks=host_callbacks or _NullProjectsOverviewHostCallbacks(),
        )
        self._presenter.attach()
        self.destroyed.connect(lambda: self._presenter.detach())

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
        self._presenter.set_project(project)

    def _on_milestones_clicked(self) -> None:
        if self._project:
            self.manage_milestones_requested.emit(self._project)

    def get_project(self) -> dict | None:
        """Liefert das aktuell angezeigte Projekt."""
        return self._project

    def _on_set_active(self) -> None:
        if self._project:
            self.set_active_requested.emit(self._project)
        self._presenter.request_set_active_project()

    def _on_edit_clicked(self) -> None:
        if self._project:
            self.edit_project_requested.emit(self._project)

    def _on_delete_clicked(self) -> None:
        if self._project:
            self.delete_project_requested.emit(self._project)

    def _on_chat_clicked(self, chat_id: int) -> None:
        self._presenter.request_open_chat(chat_id)

    def _on_prompt_clicked(self, prompt_id: int) -> None:
        self._presenter.request_open_prompt_studio(prompt_id)

    def _on_source_clicked(self, source_path: str) -> None:
        self._presenter.request_open_knowledge(source_path)

    def _on_quick_new_chat(self) -> None:
        self._presenter.request_open_chat()

    def _on_quick_add_source(self) -> None:
        self._presenter.request_open_knowledge()

    def _on_quick_new_prompt(self) -> None:
        self._presenter.request_open_prompt_studio()

    def _on_quick_open_knowledge(self) -> None:
        self._presenter.request_open_knowledge()

    def _on_quick_open_prompt_studio(self) -> None:
        self._presenter.request_open_prompt_studio()

    def _on_quick_open_agents(self) -> None:
        self._presenter.request_open_agent_tasks()

    def _on_quick_open_workflows(self) -> None:
        self._presenter.request_open_workflows()

    def apply_overview_loading(self) -> None:
        if self._project is None:
            self._empty_label.setText("Projekt wird geladen…")
            self._empty_label.show()
            self._content.hide()

    def apply_overview_empty(self, message: str | None = None) -> None:
        self._empty_label.setText(message or "Projekt auswählen oder neues Projekt anlegen.")
        self._empty_label.show()
        self._content.hide()
        self._header_card.set_project(None)
        self._stats_panel.set_stats(0, 0, 0, 0)
        self._activity_panel.set_activity([], [], [])
        self._mon_body.setText("—")
        self._ctrl_budget.hide()
        self._ctrl_effort.hide()
        self._ctrl_next.setText("Nächster Meilenstein: —")
        self._ctrl_counts.setText("Offen: — · Überfällig: —")
        self._ctrl_upcoming.hide()

    def apply_overview_error(self, message: str | None = None) -> None:
        self._empty_label.setText(message or "Projektübersicht konnte nicht geladen werden.")
        self._empty_label.show()
        self._content.hide()

    def apply_overview_state(self, state: ProjectOverviewState) -> None:
        self._empty_label.hide()
        self._content.show()
        self._header_card.set_overview(
            state.core,
            budget_label=state.controlling.budget_label,
            effort_label=state.controlling.effort_label,
        )
        self._stats_panel.set_stats(
            state.stats.workflow_count,
            state.stats.chat_count,
            state.stats.agent_count,
            state.stats.file_count,
        )
        self._btn_activate.setEnabled(state.can_set_active and not state.is_active_project)
        self._btn_activate.setText(
            "Aktives Projekt" if state.is_active_project else "Als aktives Projekt setzen"
        )
        self._mon_body.setText(
            "\n".join(state.monitoring.summary_lines)
            if state.monitoring.summary_lines
            else (state.monitoring.fallback_text or "—")
        )
        self._activity_panel.set_activity(
            [
                {
                    "id": item.chat_id,
                    "title": item.title,
                    "last_activity": item.updated_at_label,
                }
                for item in state.activity.recent_chats
            ],
            [
                {
                    "id": item.prompt_id,
                    "title": item.title,
                    "updated_at": item.updated_at_label,
                }
                for item in state.activity.recent_prompts
            ],
            [
                {
                    "path": item.source_path,
                    "name": item.display_name,
                    "status": item.status_label,
                }
                for item in state.activity.recent_sources
            ],
        )
        if state.controlling.budget_label:
            self._ctrl_budget.setText(f"Budget: {state.controlling.budget_label}")
            self._ctrl_budget.show()
        else:
            self._ctrl_budget.hide()
        if state.controlling.effort_label:
            self._ctrl_effort.setText(f"Aufwandsschätzung: {state.controlling.effort_label}")
            self._ctrl_effort.show()
        else:
            self._ctrl_effort.hide()
        self._ctrl_next.setText(f"Nächster Meilenstein: {state.controlling.next_milestone_label or '—'}")
        self._ctrl_counts.setText(state.controlling.milestone_counts_label or "Offen: — · Überfällig: —")
        if state.controlling.upcoming_milestone_lines:
            self._ctrl_upcoming.setText(
                "Demnächst:\n" + "\n".join(f"• {line}" for line in state.controlling.upcoming_milestone_lines)
            )
            self._ctrl_upcoming.show()
        else:
            self._ctrl_upcoming.hide()


class _NullProjectsOverviewHostCallbacks:
    def on_project_selection_changed(self, payload) -> None:
        del payload

    def on_request_open_chat(self, project_id: int, chat_id: int | None = None) -> None:
        del project_id, chat_id

    def on_request_open_prompt_studio(self, project_id: int, prompt_id: int | None = None) -> None:
        del project_id, prompt_id

    def on_request_open_knowledge(self, project_id: int, source_path: str | None = None) -> None:
        del project_id, source_path

    def on_request_open_workflows(self, project_id: int) -> None:
        del project_id

    def on_request_open_agent_tasks(self, project_id: int) -> None:
        del project_id

    def on_request_set_active_project(self, project_id: int | None) -> None:
        del project_id
