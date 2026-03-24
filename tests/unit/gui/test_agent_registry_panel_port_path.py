"""AgentRegistryPanel — Port-Pfad vs. Legacy (Slice 1)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.agents.agent_profile import AgentProfile
from app.gui.domains.operations.agent_tasks.panels.agent_registry_panel import AgentRegistryPanel
from app.ui_application.adapters.service_agent_tasks_registry_adapter import AgentTasksRegistrySnapshot
from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorReadDto
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentRegistryRowDto,
    AgentTasksRegistryViewState,
    agent_tasks_selection_idle_state,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelDto, LoadAgentTaskPanelCommand


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0
        self.last_registry_snapshot: AgentTasksRegistrySnapshot | None = None

    def load_registry_view(self, project_id: int | None) -> AgentTasksRegistryViewState:
        self.calls += 1
        del project_id
        prof = AgentProfile(id="p1", name="One")
        self.last_registry_snapshot = AgentTasksRegistrySnapshot(
            agents=[prof],
            profiles_by_id={"p1": prof},
            summaries_by_id={},
        )
        return AgentTasksRegistryViewState(
            phase="ready",
            rows=(AgentRegistryRowDto(agent_id="p1", list_item_text="One"),),
        )

    def load_agent_task_selection_detail(self, command) -> object:  # noqa: ANN001
        del command
        return agent_tasks_selection_idle_state()

    def load_agent_tasks_inspector_state(self, agent_id: str, project_id: int | None) -> AgentTasksInspectorReadDto:
        del agent_id, project_id
        return AgentTasksInspectorReadDto()

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        del command
        return AgentTaskPanelDto(agent_id="", task_count=0, recent_tasks=())


def test_legacy_refresh_calls_agent_service(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def list_agents_for_project(self, *a, **k):  # noqa: ANN002
            called.append("list")
            return []

    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _S(),
    )
    p = AgentRegistryPanel(agent_tasks_registry_port=None)
    p.refresh(project_id=1, summaries_by_id={})
    assert called == ["list"]


def test_port_path_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = AgentRegistryPanel(agent_tasks_registry_port=port)
    p.refresh(project_id=3)
    assert port.calls == 1
    assert p._list.count() == 1
