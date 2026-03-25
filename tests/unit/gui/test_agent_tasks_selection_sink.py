"""AgentTasksSelectionSink — Slice 2."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.agent_tasks.agent_tasks_selection_sink import AgentTasksSelectionSink
from app.gui.domains.operations.agent_tasks.panels.agent_operations_detail_panel import (
    AgentOperationsDetailPanel,
)
from app.qa.operations_models import AgentOperationsSummary
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentTasksOperationsSummaryDto,
    AgentTasksSelectionViewState,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


def test_sink_idle_clears_panel(qapp) -> None:
    panel = AgentOperationsDetailPanel()
    panel.set_summary(
        AgentOperationsSummary(
            agent_id="x",
            slug="",
            display_name="",
            status="",
            assigned_model="",
            model_role="",
            cloud_allowed=False,
            last_activity_at=None,
            last_activity_source="none",
        )
    )
    sink = AgentTasksSelectionSink(panel)
    sink.apply_selection_state(AgentTasksSelectionViewState(phase="idle"))
    assert panel._summary is None  # noqa: SLF001
    assert "auswählen" in panel._body.text().lower()  # noqa: SLF001


def test_sink_ready_maps_dto(qapp) -> None:
    panel = AgentOperationsDetailPanel()
    dto = AgentTasksOperationsSummaryDto(
        agent_id="a1",
        slug="slug",
        display_name="DN",
        status="active",
        assigned_model="m",
        model_role="r",
        cloud_allowed=True,
        last_activity_at=None,
        last_activity_source="none",
        workflow_definition_ids=("wf1",),
    )
    AgentTasksSelectionSink(panel).apply_selection_state(AgentTasksSelectionViewState(phase="ready", summary=dto))
    assert panel._summary is not None  # noqa: SLF001
    assert panel._summary.agent_id == "a1"  # noqa: SLF001
    assert "slug" in panel._body.text().lower()  # noqa: SLF001


def test_sink_error_shows_message(qapp) -> None:
    panel = AgentOperationsDetailPanel()
    err = SettingsErrorInfo(code="c", message="read failed")
    AgentTasksSelectionSink(panel).apply_selection_state(
        AgentTasksSelectionViewState(phase="error", error=err),
    )
    assert "read failed" in panel._body.text()  # noqa: SLF001
