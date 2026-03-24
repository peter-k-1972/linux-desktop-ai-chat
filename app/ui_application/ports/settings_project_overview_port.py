"""
SettingsProjectOverviewPort — aktives Projekt für Settings-Kategorie (Qt-frei, read-only).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.settings_project_overview import SettingsActiveProjectViewState


@runtime_checkable
class SettingsProjectOverviewPort(Protocol):
    def load_active_project_view_state(self) -> SettingsActiveProjectViewState:
        """Kontext-Manager + Projekt-Service; keine Exceptions nach außen (error-Mode)."""
        ...
