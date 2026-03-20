"""
AgentListPanel – Agent Library list for the Agent Workspace.

Lists agents belonging to the active project.
Each agent displays: name, model, prompt (preview), number of tools.
+ Create Agent button. Selecting an agent opens the agent editor.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QLabel,
)
from PySide6.QtCore import Qt, Signal

from app.agents.agent_profile import AgentProfile
from app.gui.domains.control_center.agents_ui.agent_list_item import AgentListItem
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class AgentListPanel(QWidget):
    """Agent Library list – project-scoped agents with Create Agent button."""

    agent_selected = Signal(object)  # AgentProfile
    create_agent_requested = Signal()

    def __init__(self, parent=None, *, theme: str = "dark"):
        super().__init__(parent)
        self.theme = theme  # For API compatibility with AgentManagerPanel
        self.setObjectName("agentListPanel")
        self._agents: list[AgentProfile] = []
        self._current_agent_id: Optional[str] = None
        self._project_id: Optional[int] = None
        self._item_widgets: list[tuple[AgentListItem, AgentProfile]] = []
        self._setup_ui()
        self._connect_project_context()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header + Create Agent button
        header = QHBoxLayout()
        title = QLabel("Agent Library")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        header.addWidget(title)
        header.addStretch()

        self._btn_create = QPushButton("+ Create Agent")
        self._btn_create.setObjectName("createAgentButton")
        self._btn_create.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_create.setEnabled(False)
        self._btn_create.setStyleSheet("""
            #createAgentButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 500;
            }
            #createAgentButton:hover { background: #1d4ed8; }
            #createAgentButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_create.clicked.connect(self._on_create_agent)
        header.addWidget(self._btn_create)
        layout.addLayout(header)

        # Scroll area with agent list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)

        self._empty_label = QLabel("Keine Agenten. Projekt auswählen oder Agent erstellen.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 24px;")
        self._empty_label.hide()

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            from app.core.context.project_context_manager import get_project_context_manager
            subscribe_project_events(self._on_project_context_changed)
            mgr = get_project_context_manager()
            pid = mgr.get_active_project_id()
            self._on_project_context_changed({"project_id": pid})
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        project_id = payload.get("project_id")
        self._project_id = project_id
        self._btn_create.setEnabled(project_id is not None)
        self._load_agents()

    def _load_agents(self) -> None:
        """Load agents for the active project."""
        try:
            from app.agents.agent_service import get_agent_service
            svc = get_agent_service()
            self._agents = svc.list_for_project(
                project_id=self._project_id,
                filter_text="",
            )
        except Exception:
            self._agents = []
        self._render_list()

    def _render_list(self) -> None:
        """Build list of AgentListItem widgets."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._item_widgets.clear()

        if not self._agents:
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText(
                "Keine Agenten in diesem Projekt." if self._project_id else "Bitte Projekt auswählen."
            )
            self._empty_label.show()
            self._list_layout.addStretch()
            return

        self._empty_label.hide()
        for profile in self._agents:
            item = AgentListItem(profile, active=(profile.id == self._current_agent_id))
            item.setCursor(Qt.CursorShape.PointingHandCursor)
            item.clicked.connect(self._on_item_clicked)
            self._list_layout.addWidget(item)
            self._item_widgets.append((item, profile))
        self._list_layout.addStretch()

    def _on_item_clicked(self, profile: AgentProfile) -> None:
        """Handle agent item click – select and open editor."""
        self._current_agent_id = profile.id
        for item, _ in self._item_widgets:
            item.set_active(item.profile.id == profile.id)
        self.agent_selected.emit(profile)

    def _on_create_agent(self) -> None:
        self.create_agent_requested.emit()

    def set_agents(self, agents: list[AgentProfile]) -> None:
        """Set agents directly (alternative to project-based load)."""
        self._agents = list(agents)
        self._render_list()

    def set_current_agent(self, profile: Optional[AgentProfile]) -> None:
        """Set the currently selected agent."""
        self._current_agent_id = profile.id if profile else None
        for item, p in self._item_widgets:
            item.set_active(p.id == self._current_agent_id)

    def get_selected(self) -> AgentProfile | None:
        """Return the currently selected agent."""
        for _, p in self._item_widgets:
            if p.id == self._current_agent_id:
                return p
        return None

    def refresh(self) -> None:
        """Reload agents from service."""
        self._load_agents()

    @property
    def list_widget(self):
        """Test compatibility: QListWidget-like adapter. count() and item(i).data(UserRole) -> profile."""
        from PySide6.QtCore import Qt

        class _ListAdapter:
            def __init__(self, panel):
                self._panel = panel

            def count(self) -> int:
                return len(self._panel._item_widgets)

            def item(self, i: int):
                if 0 <= i < len(self._panel._item_widgets):
                    _, profile = self._panel._item_widgets[i]
                    return _ItemAdapter(profile)
                return None

            def setCurrentItem(self, item) -> None:
                """No-op for test compatibility; selection is via _on_agent_selected."""
                pass

        class _ItemAdapter:
            def __init__(self, profile):
                self._profile = profile

            def data(self, role):
                if role == Qt.ItemDataRole.UserRole:
                    return self._profile
                return None

        return _ListAdapter(self)
