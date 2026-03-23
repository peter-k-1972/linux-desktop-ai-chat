"""
AgentRegistryPanel – Liste vorhandener Agenten (R2: alle Status, Issue-Hinweis).

Daten kommen aus AgentService + AgentOperationsReadService (über summaries).
"""

from typing import Dict, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, Signal
from app.gui.shared import BasePanel
from app.agents.agent_profile import AgentProfile
from app.qa.operations_models import AgentOperationsSummary


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
        self._summaries_by_id: Dict[str, AgentOperationsSummary] = {}
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

    def refresh(
        self,
        project_id: Optional[int] = None,
        summaries_by_id: Optional[Dict[str, AgentOperationsSummary]] = None,
    ) -> None:
        """Lädt Agenten neu. summaries_by_id: R2-Read-Service (optional)."""
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
                item = QListWidgetItem("Keine Agenten – Seed ausführen?")
                self._list.addItem(item)
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
            item = QListWidgetItem("Agenten konnten nicht geladen werden")
            self._list.addItem(item)

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
