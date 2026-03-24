"""AgentTasksWorkspace — Inspector Port-Pfad (Slice 3)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.agents.agent_task_runner import AgentTaskResult


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


class _Host:
    def __init__(self) -> None:
        self.packets: list = []

    def set_content(self, content, content_token=None) -> None:
        self.packets.append(content)


def test_refresh_inspector_port_path_uses_presenter(qapp) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    calls = []
    ws = AgentTasksWorkspace()
    ws.setup_inspector(_Host(), content_token=None)
    ws._inspector_presenter.handle_command = lambda c: calls.append(c)  # type: ignore[method-assign]
    ws._inspector_focus_agent_id = "z1"
    ws._last_project_id = 4
    ws._sending = False
    ws._refresh_inspector(None)
    assert len(calls) == 1
    assert calls[0].agent_id == "z1"
    assert calls[0].project_id == 4


def test_refresh_inspector_legacy_builds_classic_widget(qapp) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace
    from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector

    host = _Host()
    ws = AgentTasksWorkspace()
    ws.setup_inspector(host)
    res = AgentTaskResult(
        task_id="t",
        agent_id="a",
        agent_name="N",
        prompt="p",
        response="r",
        model="m",
        success=True,
        duration_sec=1.0,
    )
    ws._refresh_inspector_legacy(res)
    assert isinstance(host.packets[-1], AgentTasksInspector)
