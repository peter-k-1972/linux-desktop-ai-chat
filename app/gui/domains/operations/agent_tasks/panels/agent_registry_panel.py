"""
AgentRegistryPanel – Liste vorhandener Agenten.

Zeigt Agentname, Rolle, Modell, Status.
Projektbezogen: Ohne Projekt wird "Bitte Projekt auswählen" angezeigt.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from app.gui.shared import BasePanel
from app.agents.agent_profile import AgentProfile


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentRegistryPanel(BasePanel):
    """Liste aller Agenten aus AgentService."""

    agent_selected = Signal(object)  # AgentProfile

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentRegistryPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

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

    def _on_item_clicked(self, item: QListWidgetItem):
        profile = item.data(Qt.ItemDataRole.UserRole)
        if profile and isinstance(profile, AgentProfile):
            self.agent_selected.emit(profile)

    def refresh(self, project_id: Optional[int] = None) -> None:
        """Lädt Agenten neu. Ohne Projekt: Empty State 'Bitte Projekt auswählen'."""
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
            agents = service.list_agents_for_project(project_id, status="active")
            if not agents:
                agents = service.list_agents_for_project(project_id)
            for profile in agents:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, profile)
                label = f"{profile.effective_display_name}"
                if profile.role:
                    label += f" · {profile.role}"
                if profile.assigned_model:
                    label += f"\n  Modell: {profile.assigned_model}"
                item.setText(label)
                self._list.addItem(item)
        except Exception:
            item = QListWidgetItem("Keine Agenten – Seed ausführen?")
            self._list.addItem(item)
