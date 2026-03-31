"""
ProjectsOverviewCommandPort — minimale Commands für Projects Slice 1.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.projects_overview import CommandResult


@runtime_checkable
class ProjectsOverviewCommandPort(Protocol):
    def select_project(self, project_id: int | None) -> None:
        ...

    def set_active_project(self, project_id: int | None) -> CommandResult:
        ...
