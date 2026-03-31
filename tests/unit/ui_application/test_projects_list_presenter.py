"""ProjectsListPresenter — Slice 1, Qt-frei."""

from __future__ import annotations

from app.ui_application.presenters.projects_list_presenter import ProjectsListPresenter
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ActiveProjectSnapshot,
    ProjectListItem,
    ProjectListLoadResult,
    SubscriptionHandle,
)


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def show_loading(self) -> None:
        self.calls.append(("loading", None))

    def show_items(
        self,
        items: tuple[ProjectListItem, ...],
        selected_project_id: int | None,
    ) -> None:
        self.calls.append(("items", (items, selected_project_id)))

    def show_empty(self, reason: str | None) -> None:
        self.calls.append(("empty", reason))

    def show_error(self, message: str | None) -> None:
        self.calls.append(("error", message))


class _Port:
    def __init__(self, items: tuple[ProjectListItem, ...]) -> None:
        self.items = items
        self.load_calls: list[tuple[str, int | None, int | None]] = []
        self.listener = None

    def load_project_list(
        self,
        filter_text: str,
        *,
        active_project_id: int | None = None,
        selected_project_id: int | None = None,
    ) -> ProjectListLoadResult:
        self.load_calls.append((filter_text, active_project_id, selected_project_id))
        return ProjectListLoadResult(items=self.items, empty_reason=None if self.items else "no_projects")

    def load_active_project_snapshot(self) -> ActiveProjectSnapshot:
        return ActiveProjectSnapshot(active_project_id=2, is_any_project_active=True)

    def subscribe_active_project_changed(self, listener):
        self.listener = listener
        return SubscriptionHandle()


def _item(project_id: int, name: str) -> ProjectListItem:
    return ProjectListItem(
        project_id=project_id,
        display_name=name,
        secondary_text="",
        lifecycle_label="Aktiv",
        status_label="active",
        last_activity_label="01.01.2026 10:00",
        is_active=False,
        is_selected=False,
    )


def test_presenter_attach_loads_and_selects_first_item() -> None:
    sink = _Sink()
    port = _Port((_item(1, "A"), _item(2, "B")))
    presenter = ProjectsListPresenter(sink, port)

    presenter.attach()

    assert sink.calls[0] == ("loading", None)
    kind, payload = sink.calls[1]
    assert kind == "items"
    _items, selected_project_id = payload
    assert selected_project_id == 1
    assert port.load_calls[-1] == ("", 2, None)


def test_presenter_keeps_existing_selection_when_still_visible() -> None:
    sink = _Sink()
    port = _Port((_item(1, "A"), _item(2, "B")))
    presenter = ProjectsListPresenter(sink, port)
    presenter.set_selected_project_id(2)

    presenter.refresh()

    kind, payload = sink.calls[-1]
    assert kind == "items"
    _items, selected_project_id = payload
    assert selected_project_id == 2


def test_presenter_clears_selection_when_filtered_selection_disappears() -> None:
    sink = _Sink()
    port = _Port((_item(1, "A"),))
    presenter = ProjectsListPresenter(sink, port)
    presenter.set_selected_project_id(99)

    presenter.refresh()

    kind, payload = sink.calls[-1]
    assert kind == "items"
    _items, selected_project_id = payload
    assert selected_project_id is None


def test_presenter_reloads_on_active_project_event() -> None:
    sink = _Sink()
    port = _Port((_item(1, "A"),))
    presenter = ProjectsListPresenter(sink, port)
    presenter.attach()

    assert port.listener is not None
    before = len(port.load_calls)
    port.listener(
        ActiveProjectChangedPayload(
            active_project_id=5,
            is_any_project_active=True,
        )
    )

    assert len(port.load_calls) == before + 1
    assert port.load_calls[-1][1] == 5
