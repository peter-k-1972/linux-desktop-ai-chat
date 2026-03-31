"""
ProjectOverviewSink — spiegelt ``ProjectOverviewState`` auf ``ProjectOverviewPanel``.
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.projects_overview import ProjectOverviewState


class ProjectOverviewSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def show_loading(self) -> None:
        self._panel.apply_overview_loading()

    def show_empty(self, message: str | None = None) -> None:
        self._panel.apply_overview_empty(message)

    def show_error(self, message: str | None = None) -> None:
        self._panel.apply_overview_error(message)

    def show_overview(self, state: ProjectOverviewState) -> None:
        self._panel.apply_overview_state(state)
