"""ProjectInspectorPresenter — Slice 1, Qt-frei."""

from __future__ import annotations

from app.ui_application.presenters.project_inspector_presenter import ProjectInspectorPresenter
from app.ui_contracts.workspaces.projects_overview import (
    ProjectInspectorState,
    ProjectsPortError,
)


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object | None]] = []

    def show_loading(self) -> None:
        self.calls.append(("loading", None))

    def show_empty(self, message: str | None = None) -> None:
        self.calls.append(("empty", message))

    def show_error(self, message: str | None = None) -> None:
        self.calls.append(("error", message))

    def show_inspector(self, state: ProjectInspectorState) -> None:
        self.calls.append(("inspector", state))


class _Port:
    def __init__(self, state: ProjectInspectorState | None = None) -> None:
        self.state = _state() if state is None else state
        self.load_calls: list[int] = []

    def load_project_inspector(self, project_id: int) -> ProjectInspectorState | None:
        self.load_calls.append(project_id)
        return self.state


def _state(project_id: int = 7) -> ProjectInspectorState:
    return ProjectInspectorState(
        project_id=project_id,
        title="Projekt X",
        status_label="active",
        lifecycle_label="Aktiv",
        context_policy_caption="Architektur",
        context_rules_narrative="Regel A",
        description_display="Beschreibung",
        customer_name="Acme",
        internal_code="AC-7",
        external_reference="REF-7",
        updated_at_label="31.03.2026 12:00",
    )


def test_presenter_shows_empty_without_selection() -> None:
    sink = _Sink()
    presenter = ProjectInspectorPresenter(sink, _Port())

    presenter.set_project(None)

    assert sink.calls[-1] == ("empty", None)


def test_presenter_loads_state_for_dict_selection() -> None:
    sink = _Sink()
    port = _Port()
    presenter = ProjectInspectorPresenter(sink, port)

    presenter.set_project({"project_id": 7, "name": "Projekt X"})

    assert port.load_calls == [7]
    assert sink.calls[0] == ("loading", None)
    assert sink.calls[-1][0] == "inspector"


def test_presenter_loads_state_for_int_selection() -> None:
    sink = _Sink()
    port = _Port()
    presenter = ProjectInspectorPresenter(sink, port)

    presenter.set_project(7)

    assert port.load_calls == [7]
    assert sink.calls[-1][0] == "inspector"


def test_presenter_shows_empty_when_port_returns_none() -> None:
    sink = _Sink()
    port = _Port()
    port.state = None
    presenter = ProjectInspectorPresenter(sink, port)

    presenter.set_project({"project_id": 7})

    assert sink.calls[-1] == ("empty", "Projekt konnte nicht geladen werden.")


def test_presenter_shows_error_for_port_error() -> None:
    class _ErrorPort:
        def load_project_inspector(self, project_id: int) -> ProjectInspectorState | None:
            del project_id
            raise ProjectsPortError("inspect_failed", "kaputt")

    sink = _Sink()
    presenter = ProjectInspectorPresenter(sink, _ErrorPort())

    presenter.set_project({"project_id": 7})

    assert sink.calls[-1] == ("error", "kaputt")


def test_presenter_refresh_reuses_current_selection() -> None:
    sink = _Sink()
    port = _Port()
    presenter = ProjectInspectorPresenter(sink, port)
    presenter.set_project({"project_id": 7})

    presenter.refresh()

    assert port.load_calls == [7, 7]
