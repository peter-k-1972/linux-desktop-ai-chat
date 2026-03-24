"""
AgentRegistryPanel – Liste vorhandener Agenten (R2: alle Status, Issue-Hinweis).

Slice 1: Mit ``agent_tasks_registry_port``: Laden über Presenter → Port → Adapter.
Legacy: ``agent_tasks_registry_port=None`` — direkter Service wie zuvor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, Signal

from app.gui.domains.operations.agent_tasks.agent_tasks_registry_sink import AgentTasksRegistrySink
from app.gui.shared import BasePanel
from app.agents.agent_profile import AgentProfile
from app.qa.operations_models import AgentOperationsSummary
from app.ui_application.presenters.agent_tasks_registry_presenter import AgentTasksRegistryPresenter
from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTasksRegistryCommand

if TYPE_CHECKING:
    from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentRegistryPanel(BasePanel):
    """Liste aller Agenten aus AgentService."""

    agent_selected = Signal(object)  # AgentProfile

    def __init__(self, parent=None, *, agent_tasks_registry_port: AgentTasksRegistryPort | None = None):
        super().__init__(parent)
        self.setObjectName("agentRegistryPanel")
        self.setMinimumHeight(180)
        self._agent_tasks_registry_port = agent_tasks_registry_port
        self._registry_sink: AgentTasksRegistrySink | None = None
        self._registry_presenter: AgentTasksRegistryPresenter | None = None
        self._summaries_by_id: Dict[str, AgentOperationsSummary] = {}
        self._setup_ui()

        if agent_tasks_registry_port is not None:
            self._feedback = QLabel("")
            self._feedback.setObjectName("agentTasksRegistryFeedback")
            self._feedback.setWordWrap(True)
            self._feedback.hide()
            layout = self.layout()
            if layout is not None:
                layout.insertWidget(1, self._feedback)
            self._registry_sink = AgentTasksRegistrySink(self._list, self._feedback)
            self._registry_presenter = AgentTasksRegistryPresenter(
                self._registry_sink,
                agent_tasks_registry_port,
            )

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agenten")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("agentRegistryList")
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 8px; border-radius: 6px; }"
            "QListWidget::item:selected { background: #ede9fe; color: #5b21b6; }"
            "QListWidget::item:hover { background: #f5f3ff; }"
        )
        layout.addWidget(self._list, 1)

    def _use_port_path(self) -> bool:
        return self._registry_presenter is not None

    def uses_port_driven_registry(self) -> bool:
        """True wenn Registry über Port/Presenter läuft (Slice-1/2-Hauptpfad)."""
        return self._registry_presenter is not None

    def _on_item_clicked(self, item: QListWidgetItem):
        profile = item.data(Qt.ItemDataRole.UserRole)
        if profile and isinstance(profile, AgentProfile):
            self.agent_selected.emit(profile)

    def refresh(
        self,
        project_id: Optional[int] = None,
        summaries_by_id: Optional[Dict[str, AgentOperationsSummary]] = None,
    ) -> None:
        """Lädt Agenten neu. ``summaries_by_id`` nur im Legacy-Pfad."""
        if self._use_port_path():
            assert self._registry_presenter is not None
            self._registry_presenter.handle_command(LoadAgentTasksRegistryCommand(project_id))
            return
        self._refresh_legacy(project_id, summaries_by_id)

    def _refresh_legacy(
        self,
        project_id: Optional[int],
        summaries_by_id: Optional[Dict[str, AgentOperationsSummary]],
    ) -> None:
        self._summaries_by_id = dict(summaries_by_id or {})
        self._list.clear()
        if project_id is None:
            item = QListWidgetItem("Bitte Projekt auswählen")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self._list.addItem(item)
            return
        try:
            from app.services.agent_service import get_agent_service

            service = get_agent_service()
            agents = service.list_agents_for_project(
                project_id,
                department=None,
                status=None,
                filter_text="",
            )
            if not agents:
                self._list.addItem(QListWidgetItem("Keine Agenten – Seed ausführen?"))
                return
            for profile in agents:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, profile)
                label = f"{profile.effective_display_name}"
                if profile.role:
                    label += f" · {profile.role}"
                st = (profile.status or "").strip()
                if st:
                    label += f"\n  Status: {st}"
                if profile.assigned_model:
                    label += f"\n  Modell: {profile.assigned_model}"
                if profile.id:
                    s = self._summaries_by_id.get(profile.id)
                    if s and s.issues:
                        label += f"\n  ⚠ {len(s.issues)} Hinweis(e)"
                item.setText(label)
                self._list.addItem(item)
        except Exception:
            self._list.addItem(QListWidgetItem("Agenten konnten nicht geladen werden"))

    def select_agent_by_id(self, agent_id: str) -> None:
        """Wählt einen Agenten nach ID (R2 Pending-Kontext)."""
        aid = (agent_id or "").strip()
        if not aid:
            return
        for i in range(self._list.count()):
            it = self._list.item(i)
            prof = it.data(Qt.ItemDataRole.UserRole)
            if isinstance(prof, AgentProfile) and prof.id == aid:
                self._list.setCurrentItem(it)
                self.agent_selected.emit(prof)
                return
