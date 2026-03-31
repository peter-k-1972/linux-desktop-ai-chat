"""
ProjectsListPresenter — Slice-1-Read-Pfad für ``ProjectListPanel``.
"""

from __future__ import annotations

from typing import Protocol

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ProjectListItem,
    ProjectsPortError,
    SubscriptionHandle,
)


class ProjectsListUiSink(Protocol):
    def show_loading(self) -> None:
        ...

    def show_items(
        self,
        items: tuple[ProjectListItem, ...],
        selected_project_id: int | None,
    ) -> None:
        ...

    def show_empty(self, reason: str | None) -> None:
        ...

    def show_error(self, message: str | None) -> None:
        ...


class ProjectsListPresenter(BasePresenter):
    def __init__(
        self,
        sink: ProjectsListUiSink,
        port: ProjectsOverviewReadPort,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._filter_text = ""
        self._selected_project_id: int | None = None
        self._active_project_id: int | None = None
        self._subscription: SubscriptionHandle | None = None

    def attach(self) -> None:
        super().attach()
        try:
            snap = self._port.load_active_project_snapshot()
            self._active_project_id = snap.active_project_id
        except Exception:
            self._active_project_id = None
        try:
            self._subscription = self._port.subscribe_active_project_changed(
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

    def set_filter_text(self, filter_text: str) -> None:
        self._filter_text = filter_text
        self.refresh()

    def set_selected_project_id(self, project_id: int | None) -> None:
        self._selected_project_id = project_id

    def refresh(self) -> None:
        self._sink.show_loading()
        try:
            result = self._port.load_project_list(
                self._filter_text,
                active_project_id=self._active_project_id,
                selected_project_id=self._selected_project_id,
            )
        except ProjectsPortError as exc:
            self._sink.show_error(exc.message)
            return
        except Exception as exc:
            self._sink.show_error(str(exc) or "Projektliste konnte nicht geladen werden.")
            return

        selected_project_id = self._resolve_selected_project_id(result.items)
        self._selected_project_id = selected_project_id
        if result.items:
            self._sink.show_items(result.items, selected_project_id)
            return
        self._sink.show_empty(result.empty_reason)

    def _resolve_selected_project_id(
        self,
        items: tuple[ProjectListItem, ...],
    ) -> int | None:
        if not items:
            return None
        ids = {item.project_id for item in items}
        if self._selected_project_id is not None:
            return self._selected_project_id if self._selected_project_id in ids else None
        return items[0].project_id

    def _on_active_project_changed(self, payload: ActiveProjectChangedPayload) -> None:
        self._active_project_id = payload.active_project_id
        self.refresh()
