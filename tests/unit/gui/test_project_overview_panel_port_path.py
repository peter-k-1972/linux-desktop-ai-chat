"""ProjectOverviewPanel — Slice-1-Port- und Callback-Pfad."""

from __future__ import annotations

from app.gui.domains.operations.projects.panels.project_overview_panel import ProjectOverviewPanel
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    CommandResult,
    ProjectActivityChatItem,
    ProjectActivityPromptItem,
    ProjectActivitySourceItem,
    ProjectActivityView,
    ProjectControllingView,
    ProjectCoreView,
    ProjectMonitoringView,
    ProjectOverviewState,
    ProjectSelectionChangedPayload,
    ProjectStatsView,
    SubscriptionHandle,
)


def _state(*, active: bool = False) -> ProjectOverviewState:
    return ProjectOverviewState(
        project_id=42,
        core=ProjectCoreView(
            project_id=42,
            name="Testprojekt",
            description_display="Beschreibung",
            lifecycle_label="Aktiv",
            status_label="active",
            default_context_policy_label="Architektur",
            customer_name="Acme",
            internal_code="AC-42",
            updated_at_label="31.03.2026 10:00",
        ),
        stats=ProjectStatsView(workflow_count=4, chat_count=5, agent_count=6, file_count=7),
        monitoring=ProjectMonitoringView(summary_lines=("Monitoring ok",), has_data=True),
        activity=ProjectActivityView(
            recent_chats=(ProjectActivityChatItem(chat_id=9, title="Chat A", updated_at_label="Heute"),),
            recent_prompts=(ProjectActivityPromptItem(prompt_id=11, title="Prompt A", updated_at_label="Heute"),),
            recent_sources=(
                ProjectActivitySourceItem(
                    source_path="/tmp/spec.md",
                    display_name="spec.md",
                    status_label="ready",
                ),
            ),
            has_any_activity=True,
        ),
        controlling=ProjectControllingView(
            budget_label="100 EUR",
            effort_label="5 h",
            next_milestone_label="Kickoff",
            milestone_counts_label="Offen: 1 · Überfällig: 0",
            upcoming_milestone_lines=("Kickoff",),
        ),
        can_set_active=not active,
        is_active_project=active,
    )


class _ReadPort:
    def __init__(self) -> None:
        self.calls: list[int] = []
        self.listener = None

    def load_project_overview(self, project_id: int) -> ProjectOverviewState | None:
        self.calls.append(project_id)
        return _state(active=False)

    def subscribe_active_project_changed(self, listener):
        self.listener = listener
        return SubscriptionHandle()


class _CommandPort:
    def __init__(self) -> None:
        self.selected: list[int | None] = []
        self.active: list[int | None] = []

    def select_project(self, project_id: int | None) -> None:
        self.selected.append(project_id)

    def set_active_project(self, project_id: int | None) -> CommandResult:
        self.active.append(project_id)
        return CommandResult(ok=True)


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


def test_project_overview_panel_uses_presenter_ports_and_callbacks(qapplication) -> None:
    read_port = _ReadPort()
    command_port = _CommandPort()
    host = _HostCallbacks()
    panel = ProjectOverviewPanel(
        read_port=read_port,
        command_port=command_port,
        host_callbacks=host,
    )

    panel.set_project({"project_id": 42, "name": "Testprojekt"})

    assert read_port.calls[-1] == 42
    assert command_port.selected[-1] == 42
    assert host.selection_payloads[-1].selected_project_id == 42
    assert panel._btn_activate.text() == "Als aktives Projekt setzen"
    assert panel._mon_body.text() == "Monitoring ok"
    assert panel._ctrl_next.text() == "Nächster Meilenstein: Kickoff"
    panel.deleteLater()


def test_project_overview_panel_routes_quick_actions_via_host_callbacks(qapplication) -> None:
    host = _HostCallbacks()
    panel = ProjectOverviewPanel(
        read_port=_ReadPort(),
        command_port=_CommandPort(),
        host_callbacks=host,
    )
    panel.set_project({"project_id": 42, "name": "Testprojekt"})

    panel._on_chat_clicked(9)
    panel._on_prompt_clicked(11)
    panel._on_source_clicked("/tmp/spec.md")
    panel._on_quick_open_workflows()
    panel._on_quick_open_agents()

    assert host.chat_calls == [(42, 9)]
    assert host.prompt_calls == [(42, 11)]
    assert host.knowledge_calls == [(42, "/tmp/spec.md")]
    assert host.workflow_calls == [42]
    assert host.agent_calls == [42]
    panel.deleteLater()


def test_project_overview_panel_set_active_uses_command_port_and_host_callback(qapplication) -> None:
    command_port = _CommandPort()
    host = _HostCallbacks()
    panel = ProjectOverviewPanel(
        read_port=_ReadPort(),
        command_port=command_port,
        host_callbacks=host,
    )
    panel.set_project({"project_id": 42, "name": "Testprojekt"})

    panel._on_set_active()

    assert command_port.active == [42]
    assert host.active_calls == [42]
    panel.deleteLater()
