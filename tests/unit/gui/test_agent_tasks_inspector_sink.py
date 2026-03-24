"""AgentTasksInspectorSink — Slice 3."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.agent_tasks.agent_tasks_inspector_sink import AgentTasksInspectorSink
from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector
from app.ui_contracts.workspaces.agent_tasks_inspector import (
    INSPECTOR_SECTION_SEP,
    AgentTasksInspectorState,
)


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
        self.packets: list[tuple[object, int | None]] = []

    def set_content(self, content, content_token=None) -> None:
        self.packets.append((content, content_token))


def test_sink_applies_ready_state(qapp) -> None:
    host = _Host()
    sink = AgentTasksInspectorSink(host, content_token=7)
    body = INSPECTOR_SECTION_SEP.join(["A", "B", "C"])
    sink.apply_inspector_state(
        AgentTasksInspectorState(phase="ready", last_result_text=body),
    )
    w, tok = host.packets[0]
    assert tok == 7
    assert isinstance(w, AgentTasksInspector)


def test_sink_error_state(qapp) -> None:
    host = _Host()
    AgentTasksInspectorSink(host).apply_inspector_state(
        AgentTasksInspectorState(phase="error", last_result_text="oops"),
    )
    w = host.packets[0][0]
    assert isinstance(w, AgentTasksInspector)
