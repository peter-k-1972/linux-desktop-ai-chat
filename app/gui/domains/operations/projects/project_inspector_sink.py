"""
ProjectInspectorSink — spiegelt ``ProjectInspectorState`` auf ``ProjectInspectorPanel``.
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.projects_overview import ProjectInspectorState


class ProjectInspectorSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def show_loading(self) -> None:
        self._panel.apply_inspector_loading()

    def show_empty(self, message: str | None = None) -> None:
        self._panel.apply_inspector_empty(message)

    def show_error(self, message: str | None = None) -> None:
        self._panel.apply_inspector_error(message)

    def show_inspector(self, state: ProjectInspectorState) -> None:
        self._panel.apply_inspector_state(state)
