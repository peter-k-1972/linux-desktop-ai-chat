"""
ProjectInspectorPresenter — Slice-1-Read-Pfad fuer ``ProjectInspectorPanel``.
"""

from __future__ import annotations

from typing import Protocol

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import ProjectInspectorState, ProjectsPortError


class ProjectInspectorUiSink(Protocol):
    def show_loading(self) -> None:
        ...

    def show_empty(self, message: str | None = None) -> None:
        ...

    def show_error(self, message: str | None = None) -> None:
        ...

    def show_inspector(self, state: ProjectInspectorState) -> None:
        ...


class ProjectInspectorPresenter(BasePresenter):
    def __init__(
        self,
        sink: ProjectInspectorUiSink,
        read_port: ProjectsOverviewReadPort,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._read_port = read_port
        self._selected_project_id: int | None = None

    def set_project(self, project: dict | int | None) -> None:
        self._selected_project_id = self._extract_project_id(project)
        self.refresh()

    def refresh(self) -> None:
        if self._selected_project_id is None:
            self._sink.show_empty()
            return
        self._sink.show_loading()
        try:
            state = self._read_port.load_project_inspector(self._selected_project_id)
        except ProjectsPortError as exc:
            self._sink.show_error(exc.message)
            return
        except Exception as exc:
            self._sink.show_error(str(exc) or "Projekt-Inspector konnte nicht geladen werden.")
            return
        if state is None:
            self._sink.show_empty("Projekt konnte nicht geladen werden.")
            return
        self._sink.show_inspector(state)

    @staticmethod
    def _extract_project_id(project: dict | int | None) -> int | None:
        if project is None:
            return None
        if isinstance(project, int):
            return project
        if isinstance(project, dict):
            project_id = project.get("project_id")
            return project_id if isinstance(project_id, int) else None
        return None
