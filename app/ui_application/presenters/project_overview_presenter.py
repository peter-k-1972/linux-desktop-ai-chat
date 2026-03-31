"""
ProjectOverviewPresenter — Slice-1-Read-/Command-Pfad fuer ``ProjectOverviewPanel``.
"""

from __future__ import annotations

from typing import Protocol

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.projects_overview_command_port import ProjectsOverviewCommandPort
from app.ui_application.ports.projects_overview_host_callbacks import ProjectsOverviewHostCallbacks
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ProjectOverviewState,
    ProjectSelectionChangedPayload,
    ProjectsPortError,
    SubscriptionHandle,
)


class ProjectOverviewUiSink(Protocol):
    def show_loading(self) -> None:
        ...

    def show_empty(self, message: str | None = None) -> None:
        ...

    def show_error(self, message: str | None = None) -> None:
        ...

    def show_overview(self, state: ProjectOverviewState) -> None:
        ...


class ProjectOverviewPresenter(BasePresenter):
    def __init__(
        self,
        sink: ProjectOverviewUiSink,
        read_port: ProjectsOverviewReadPort,
        command_port: ProjectsOverviewCommandPort,
        host_callbacks: ProjectsOverviewHostCallbacks,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._read_port = read_port
        self._command_port = command_port
        self._host_callbacks = host_callbacks
        self._selected_project_id: int | None = None
        self._selected_project_name: str | None = None
        self._subscription: SubscriptionHandle | None = None

    def attach(self) -> None:
        super().attach()
        try:
            self._subscription = self._read_port.subscribe_active_project_changed(
                self._on_active_project_changed
            )
        except Exception:
            self._subscription = None
        self.refresh()

    def detach(self) -> None:
        if self._subscription is not None:
            self._subscription.dispose()
            self._subscription = None
        super().detach()

    def set_project(self, project: dict | int | None) -> None:
        project_id, project_name = self._extract_selection(project)
        self._selected_project_id = project_id
        self._selected_project_name = project_name
        try:
            self._command_port.select_project(project_id)
        except Exception:
            pass
        self._host_callbacks.on_project_selection_changed(
            ProjectSelectionChangedPayload(
                selected_project_id=project_id,
                selected_project_name=project_name,
                selection_source="project_overview_panel",
            )
        )
        self.refresh()

    def refresh(self) -> None:
        if self._selected_project_id is None:
            self._sink.show_empty()
            return

        self._sink.show_loading()
        try:
            state = self._read_port.load_project_overview(self._selected_project_id)
        except ProjectsPortError as exc:
            self._sink.show_error(exc.message)
            return
        except Exception as exc:
            self._sink.show_error(str(exc) or "Projektuebersicht konnte nicht geladen werden.")
            return

        if state is None:
            self._sink.show_empty("Projekt konnte nicht geladen werden.")
            return
        self._sink.show_overview(state)

    def request_set_active_project(self) -> None:
        if self._selected_project_id is None:
            return
        result = self._command_port.set_active_project(self._selected_project_id)
        if not result.ok:
            self._sink.show_error(result.message or "Aktives Projekt konnte nicht gesetzt werden.")
            return
        self._host_callbacks.on_request_set_active_project(self._selected_project_id)
        self.refresh()

    def request_open_chat(self, chat_id: int | None = None) -> None:
        if self._selected_project_id is None:
            return
        self._host_callbacks.on_request_open_chat(self._selected_project_id, chat_id)

    def request_open_prompt_studio(self, prompt_id: int | None = None) -> None:
        if self._selected_project_id is None:
            return
        self._host_callbacks.on_request_open_prompt_studio(self._selected_project_id, prompt_id)

    def request_open_knowledge(self, source_path: str | None = None) -> None:
        if self._selected_project_id is None:
            return
        self._host_callbacks.on_request_open_knowledge(self._selected_project_id, source_path)

    def request_open_workflows(self) -> None:
        if self._selected_project_id is None:
            return
        self._host_callbacks.on_request_open_workflows(self._selected_project_id)

    def request_open_agent_tasks(self) -> None:
        if self._selected_project_id is None:
            return
        self._host_callbacks.on_request_open_agent_tasks(self._selected_project_id)

    def _on_active_project_changed(self, _payload: ActiveProjectChangedPayload) -> None:
        self.refresh()

    @staticmethod
    def _extract_selection(project: dict | int | None) -> tuple[int | None, str | None]:
        if project is None:
            return None, None
        if isinstance(project, int):
            return project, None
        if isinstance(project, dict):
            raw_id = project.get("project_id")
            project_id = int(raw_id) if isinstance(raw_id, int) else None
            name = (project.get("name") or "").strip() or None
            return project_id, name
        return None, None
