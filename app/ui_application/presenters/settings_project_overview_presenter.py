"""
SettingsProjectOverviewPresenter — ViewState → Body-Text für ProjectCategory.
"""

from __future__ import annotations

from typing import Protocol

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.settings_project_overview_port import SettingsProjectOverviewPort
from app.ui_contracts.workspaces.settings_project_overview import (
    RefreshSettingsActiveProjectCommand,
    SettingsActiveProjectViewState,
    SettingsProjectCategoryBodyState,
    SettingsProjectOverviewCommand,
)


class SettingsProjectOverviewUiSink(Protocol):
    def apply_body_state(self, state: SettingsProjectCategoryBodyState) -> None:
        ...


_NO_PROJECT_TEXT = (
    "Es ist kein Projekt aktiv. Wählen Sie ein Projekt in der Kopfzeile "
    "oder unter Operations → Projekte."
)
_NOT_FOUND_TEXT = "Aktives Projekt konnte nicht geladen werden."


class SettingsProjectOverviewPresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsProjectOverviewUiSink,
        port: SettingsProjectOverviewPort,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: SettingsProjectOverviewCommand) -> None:
        if isinstance(command, RefreshSettingsActiveProjectCommand):
            state = self._port.load_active_project_view_state()
            self._sink.apply_body_state(self._view_state_to_body(state))

    @staticmethod
    def _view_state_to_body(state: SettingsActiveProjectViewState) -> SettingsProjectCategoryBodyState:
        if state.mode == "no_active":
            return SettingsProjectCategoryBodyState(body_text=_NO_PROJECT_TEXT)
        if state.mode == "not_found":
            return SettingsProjectCategoryBodyState(body_text=_NOT_FOUND_TEXT)
        if state.mode == "error":
            msg = state.error_message or "Unbekannter Fehler"
            return SettingsProjectCategoryBodyState(
                body_text=f"Projektdaten konnten nicht geladen werden: {msg}"
            )
        if state.summary is None:
            return SettingsProjectCategoryBodyState(body_text=_NOT_FOUND_TEXT)
        s = state.summary
        return SettingsProjectCategoryBodyState(
            body_text=(
                f"{s.name} (ID {s.project_id})\n\n"
                f"Status: {s.status}\n"
                f"Beschreibung: {s.description_display}\n"
                f"Zugeordnete Chats: {s.chat_count}\n"
                f"Standard-Kontextpolicy (gespeichert): {s.default_context_policy_display}\n"
                f"Aktualisiert: {s.updated_at_display}"
            )
        )
