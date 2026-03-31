"""ProjectOverviewPresenter — Slice-1-Overview-Pfad."""

from __future__ import annotations

from app.ui_application.presenters.project_overview_presenter import ProjectOverviewPresenter
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    CommandResult,
    ProjectActivityView,
    ProjectControllingView,
    ProjectCoreView,
    ProjectMonitoringView,
    ProjectOverviewState,
    ProjectSelectionChangedPayload,
    ProjectStatsView,
    ProjectsPortError,
    SubscriptionHandle,
)


def _state(*, project_id: int = 7, is_active_project: bool = False, can_set_active: bool = True) -> ProjectOverviewState:
    return ProjectOverviewState(
        project_id=project_id,
        core=ProjectCoreView(
            project_id=project_id,
            name="Projekt X",
            description_display="Beschreibung",
            lifecycle_label="Aktiv",
            status_label="active",
            default_context_policy_label="Standard",
        ),
        stats=ProjectStatsView(workflow_count=1, chat_count=2, agent_count=3, file_count=4),
        monitoring=ProjectMonitoringView(summary_lines=("Alles ok",), has_data=True),
        activity=ProjectActivityView(has_any_activity=False, empty_message="Leer"),
        controlling=ProjectControllingView(
            budget_label="100 EUR",
            effort_label="5 h",
            next_milestone_label="Kickoff",
            milestone_counts_label="Offen: 1 · Überfällig: 0",
        ),
        can_set_active=can_set_active,
        is_active_project=is_active_project,
    )


class _Sink:
    def __init__(self) -> None:
        self.events: list[tuple[str, object | None]] = []

    def show_loading(self) -> None:
        self.events.append(("loading", None))

    def show_empty(self, message: str | None = None) -> None:
        self.events.append(("empty", message))

    def show_error(self, message: str | None = None) -> None:
        self.events.append(("error", message))

    def show_overview(self, state: ProjectOverviewState) -> None:
        self.events.append(("overview", state))


class _ReadPort:
    def __init__(self, state: ProjectOverviewState | None = None) -> None:
        self.state = state or _state()
        self.calls: list[int] = []
        self.listener = None

    def load_project_overview(self, project_id: int) -> ProjectOverviewState | None:
        self.calls.append(project_id)
        return self.state

    def subscribe_active_project_changed(self, listener):
        self.listener = listener
        return SubscriptionHandle()


class _CommandPort:
    def __init__(self) -> None:
        self.selected: list[int | None] = []
        self.active: list[int | None] = []
        self.result = CommandResult(ok=True, message=None)

    def select_project(self, project_id: int | None) -> None:
        self.selected.append(project_id)

    def set_active_project(self, project_id: int | None) -> CommandResult:
        self.active.append(project_id)
        return self.result


class _HostCallbacks:
    def __init__(self) -> None:
        self.selection_payloads: list[ProjectSelectionChangedPayload] = []
        self.chat_calls: list[tuple[int, int | None]] = []
        self.prompt_calls: list[tuple[int, int | None]] = []
        self.knowledge_calls: list[tuple[int, str | None]] = []
        self.workflow_calls: list[int] = []
        self.agent_calls: list[int] = []
        self.active_calls: list[int | None] = []

    def on_project_selection_changed(self, payload: ProjectSelectionChangedPayload) -> None:
        self.selection_payloads.append(payload)

    def on_request_open_chat(self, project_id: int, chat_id: int | None = None) -> None:
        self.chat_calls.append((project_id, chat_id))

    def on_request_open_prompt_studio(self, project_id: int, prompt_id: int | None = None) -> None:
        self.prompt_calls.append((project_id, prompt_id))

    def on_request_open_knowledge(self, project_id: int, source_path: str | None = None) -> None:
        self.knowledge_calls.append((project_id, source_path))

    def on_request_open_workflows(self, project_id: int) -> None:
        self.workflow_calls.append(project_id)

    def on_request_open_agent_tasks(self, project_id: int) -> None:
        self.agent_calls.append(project_id)

    def on_request_set_active_project(self, project_id: int | None) -> None:
        self.active_calls.append(project_id)


def test_presenter_loads_overview_for_selected_project() -> None:
    sink = _Sink()
    read_port = _ReadPort()
    command_port = _CommandPort()
    host = _HostCallbacks()
    presenter = ProjectOverviewPresenter(sink, read_port, command_port, host)

    presenter.attach()
    presenter.set_project({"project_id": 7, "name": "Projekt X"})

    assert command_port.selected[-1] == 7
    assert read_port.calls[-1] == 7
    assert sink.events[-1][0] == "overview"
    assert host.selection_payloads[-1].selected_project_id == 7
    assert host.selection_payloads[-1].selected_project_name == "Projekt X"


def test_presenter_shows_empty_without_selection() -> None:
    sink = _Sink()
    presenter = ProjectOverviewPresenter(sink, _ReadPort(), _CommandPort(), _HostCallbacks())

    presenter.attach()

    assert sink.events[-1][0] == "empty"


def test_presenter_shows_error_for_port_error() -> None:
    class _ErrorReadPort(_ReadPort):
        def load_project_overview(self, project_id: int) -> ProjectOverviewState | None:
            del project_id
            raise ProjectsPortError("overview_failed", "kaputt")

    sink = _Sink()
    presenter = ProjectOverviewPresenter(sink, _ErrorReadPort(), _CommandPort(), _HostCallbacks())

    presenter.set_project({"project_id": 7, "name": "Projekt X"})

    assert sink.events[-1] == ("error", "kaputt")


def test_presenter_set_active_uses_command_port_and_host_callback() -> None:
    sink = _Sink()
    read_port = _ReadPort(state=_state(is_active_project=False, can_set_active=True))
    command_port = _CommandPort()
    host = _HostCallbacks()
    presenter = ProjectOverviewPresenter(sink, read_port, command_port, host)

    presenter.set_project({"project_id": 7, "name": "Projekt X"})
    presenter.request_set_active_project()

    assert command_port.active == [7]
    assert host.active_calls == [7]


def test_presenter_routes_navigation_requests_via_host_callbacks() -> None:
    presenter = ProjectOverviewPresenter(_Sink(), _ReadPort(), _CommandPort(), host := _HostCallbacks())
    presenter.set_project({"project_id": 7, "name": "Projekt X"})

    presenter.request_open_chat(11)
    presenter.request_open_prompt_studio(12)
    presenter.request_open_knowledge("/tmp/spec.md")
    presenter.request_open_workflows()
    presenter.request_open_agent_tasks()

    assert host.chat_calls == [(7, 11)]
    assert host.prompt_calls == [(7, 12)]
    assert host.knowledge_calls == [(7, "/tmp/spec.md")]
    assert host.workflow_calls == [7]
    assert host.agent_calls == [7]


def test_presenter_refreshes_when_active_project_changes() -> None:
    sink = _Sink()
    read_port = _ReadPort()
    presenter = ProjectOverviewPresenter(sink, read_port, _CommandPort(), _HostCallbacks())
    presenter.attach()
    presenter.set_project({"project_id": 7, "name": "Projekt X"})

    read_port.listener(ActiveProjectChangedPayload(active_project_id=7, is_any_project_active=True))

    assert read_port.calls[-1] == 7
    assert sink.events[-1][0] == "overview"
