"""
ProjectsListSink — spiegelt ``ProjectListItem``-States auf ``ProjectListPanel``.
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.projects_overview import ProjectListItem


class ProjectsListSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def show_loading(self) -> None:
        self._panel.apply_project_list_loading()

    def show_items(
        self,
        items: tuple[ProjectListItem, ...],
        selected_project_id: int | None,
    ) -> None:
        self._panel.apply_project_list_items(items, selected_project_id)

    def show_empty(self, reason: str | None) -> None:
        self._panel.apply_project_list_empty(reason)

    def show_error(self, message: str | None) -> None:
        self._panel.apply_project_list_error(message)
