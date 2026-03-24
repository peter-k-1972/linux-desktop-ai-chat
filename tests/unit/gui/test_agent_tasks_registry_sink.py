"""AgentTasksRegistrySink."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget

from app.agents.agent_profile import AgentProfile
from app.gui.domains.operations.agent_tasks.agent_tasks_registry_sink import AgentTasksRegistrySink
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentRegistryRowDto,
    AgentTasksRegistryViewState,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def test_sink_loading(qapp) -> None:
    lst = QListWidget()
    fb = QLabel()
    sink = AgentTasksRegistrySink(lst, fb)
    sink.apply_full_state(AgentTasksRegistryViewState(phase="loading"))
    assert fb.isVisible()
    assert lst.count() == 0


def test_sink_ready_with_profile(qapp) -> None:
    lst = QListWidget()
    fb = QLabel()
    sink = AgentTasksRegistrySink(lst, fb)
    prof = AgentProfile(id="x", name="N")
    row = AgentRegistryRowDto(agent_id="x", list_item_text="Line")
    sink.apply_full_state(
        AgentTasksRegistryViewState(phase="ready", rows=(row,)),
        (prof,),
    )
    assert lst.count() == 1
    assert lst.item(0).data(Qt.ItemDataRole.UserRole) is prof


def test_sink_no_project(qapp) -> None:
    lst = QListWidget()
    fb = QLabel()
    sink = AgentTasksRegistrySink(lst, fb)
    sink.apply_full_state(AgentTasksRegistryViewState(phase="no_project"))
    assert lst.count() == 1
    assert "Projekt" in lst.item(0).text()


def test_sink_error(qapp) -> None:
    lst = QListWidget()
    fb = QLabel()
    sink = AgentTasksRegistrySink(lst, fb)
    sink.apply_full_state(
        AgentTasksRegistryViewState(
            phase="error",
            error=SettingsErrorInfo(code="c", message="oops"),
        ),
    )
    assert "oops" in fb.text()
