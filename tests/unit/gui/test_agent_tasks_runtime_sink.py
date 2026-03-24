"""AgentTasksRuntimeSink (Batch 6)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.agent_tasks.agent_tasks_runtime_sink import AgentTasksRuntimeSink
from app.gui.domains.operations.agent_tasks.panels.result_panel import AgentResultPanel
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskResultDto


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_sink_maps_dto_to_panel(qapp: QApplication) -> None:
    panel = AgentResultPanel()
    sink = AgentTasksRuntimeSink(panel)
    dto = StartAgentTaskResultDto(
        task_id="t",
        agent_id="a",
        agent_name="N",
        prompt="p",
        response="hello-out",
        model="m",
        success=True,
    )
    sink.apply_start_task_result(dto)
    assert "hello-out" in panel._result.toPlainText()
