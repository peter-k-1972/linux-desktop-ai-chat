"""
ProjectsOverviewHostCallbacks — Host-Klammer für Projects Slice 1.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.projects_overview import ProjectSelectionChangedPayload


@runtime_checkable
class ProjectsOverviewHostCallbacks(Protocol):
    def on_project_selection_changed(self, payload: ProjectSelectionChangedPayload) -> None:
        ...

    def on_request_open_chat(self, project_id: int, chat_id: int | None = None) -> None:
        ...

    def on_request_open_prompt_studio(self, project_id: int, prompt_id: int | None = None) -> None:
        ...

    def on_request_open_knowledge(self, project_id: int, source_path: str | None = None) -> None:
        ...

    def on_request_open_workflows(self, project_id: int) -> None:
        ...

    def on_request_open_agent_tasks(self, project_id: int) -> None:
        ...

    def on_request_set_active_project(self, project_id: int | None) -> None:
        ...
