"""
ProjectsOverviewReadPort — Qt-freier Read-Vertrag für Projects Slice 1.
"""

from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ActiveProjectSnapshot,
    ProjectInspectorState,
    ProjectListLoadResult,
    ProjectOverviewState,
    SubscriptionHandle,
)


@runtime_checkable
class ProjectsOverviewReadPort(Protocol):
    def load_project_list(
        self,
        filter_text: str,
        *,
        active_project_id: int | None = None,
        selected_project_id: int | None = None,
    ) -> ProjectListLoadResult:
        ...

    def load_project_overview(self, project_id: int) -> ProjectOverviewState | None:
        ...

    def load_project_inspector(self, project_id: int) -> ProjectInspectorState | None:
        ...

    def load_active_project_snapshot(self) -> ActiveProjectSnapshot:
        ...

    def subscribe_active_project_changed(
        self,
        listener: Callable[[ActiveProjectChangedPayload], None],
    ) -> SubscriptionHandle:
        ...
