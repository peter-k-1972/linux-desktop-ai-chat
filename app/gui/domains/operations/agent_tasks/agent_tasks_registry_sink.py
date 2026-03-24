"""
AgentTasksRegistrySink — QListWidget aus :class:`AgentTasksRegistryViewState`.

Ordnet Zeilen den Profilen aus dem Adapter-Cache zu (gleiche Reihenfolge wie ``list_agents_for_project``).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem

from app.agents.agent_profile import AgentProfile
from app.ui_contracts.workspaces.agent_tasks_registry import AgentTasksRegistryViewState


class AgentTasksRegistrySink:
    def __init__(self, list_widget: QListWidget, feedback: QLabel) -> None:
        self._list = list_widget
        self._feedback = feedback

    def apply_full_state(
        self,
        state: AgentTasksRegistryViewState,
        agent_profiles: tuple[Any, ...] = (),
    ) -> None:
        self._list.clear()
        if state.phase == "loading":
            self._feedback.setText("Agenten werden geladen …")
            self._feedback.show()
            return
        self._feedback.hide()
        if state.phase == "no_project":
            item = QListWidgetItem("Bitte Projekt auswählen")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self._list.addItem(item)
            return
        if state.phase == "error":
            msg = state.error.message if state.error else "Unbekannter Fehler."
            self._feedback.setText(msg)
            self._feedback.show()
            item = QListWidgetItem("Agenten konnten nicht geladen werden")
            self._list.addItem(item)
            return
        if state.phase == "empty":
            hint = state.empty_hint or "Keine Agenten"
            self._list.addItem(QListWidgetItem(hint))
            return
        if state.phase == "ready":
            for i, row in enumerate(state.rows):
                item = QListWidgetItem(row.list_item_text)
                prof: Any = None
                if i < len(agent_profiles):
                    prof = agent_profiles[i]
                if prof is not None and isinstance(prof, AgentProfile):
                    item.setData(Qt.ItemDataRole.UserRole, prof)
                self._list.addItem(item)
