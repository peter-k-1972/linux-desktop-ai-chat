from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from app.agents.agent_profile import AgentProfile
from app.gui.events.project_events import emit_project_context_changed
from app.ui_application.ports.qml_project_war_room_port import QmlProjectWarRoomPort
from app.workflows.models.definition import WorkflowDefinition
from python_bridge.projects.project_viewmodel import ProjectViewModel


class _FakeProjectPort(QmlProjectWarRoomPort):
    def __init__(self) -> None:
        self.projects: list[dict[str, Any]] = [
            {"project_id": 1, "name": "Alpha", "lifecycle_status": "active", "status": "ok"},
            {"project_id": 2, "name": "Beta", "lifecycle_status": "active", "status": "ok"},
        ]
        self.active_id: int | None = None
        self.set_calls: list[int] = []
        self.clear_calls: int = 0

    def list_projects(self, filter_text: str) -> list[dict[str, Any]]:
        return list(self.projects)

    def get_project_monitoring_snapshot(self, project_id: int) -> dict[str, Any]:
        return {"message_count_7d": 0, "last_activity_at": None}

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        for p in self.projects:
            if int(p["project_id"]) == int(project_id):
                return {
                    **p,
                    "description": "d",
                    "context_rules": [],
                    "default_context_mode": "inherit",
                }
        return None

    def get_recent_chats_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        return []

    def list_workflows_for_project(self, project_id: int, *, limit: int) -> list[WorkflowDefinition]:
        return []

    def list_active_agents_for_project(self, project_id: int) -> list[AgentProfile]:
        return []

    def list_files_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        return []

    def set_active_project(self, project_id: int) -> None:
        self.set_calls.append(int(project_id))
        self.active_id = int(project_id)

    def clear_active_project(self) -> None:
        self.clear_calls += 1
        self.active_id = None

    def get_active_project_id(self) -> int | None:
        return self.active_id

    def create_project(self, name: str, description: str) -> int:
        return 99

    def delete_project(self, project_id: int) -> None:
        self.projects = [p for p in self.projects if int(p["project_id"]) != int(project_id)]


@pytest.fixture
def qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_select_sets_active_and_syncs_authority(qapplication) -> None:
    port = _FakeProjectPort()
    vm = ProjectViewModel(port=port)
    try:
        vm.selectProject(2)
        assert port.active_id == 2
        assert vm.selectedProjectId == 2
        assert vm.authorityActiveProjectId == 2
        assert vm.selectionMatchesAuthority is True
    finally:
        vm.dispose()


def test_clear_selection_clears_active(qapplication) -> None:
    port = _FakeProjectPort()
    port.active_id = 1
    vm = ProjectViewModel(port=port)
    try:
        vm.selectProject(-1)
        assert port.active_id is None
        assert port.clear_calls >= 1
        assert vm.authorityActiveProjectId < 0
    finally:
        vm.dispose()


def test_reload_aligns_with_authority_active(qapplication) -> None:
    port = _FakeProjectPort()
    port.active_id = 2
    vm = ProjectViewModel(port=port)
    try:
        vm.reload()
        assert vm.selectedProjectId == 2
    finally:
        vm.dispose()


def test_external_project_event_syncs_selection(qapplication) -> None:
    port = _FakeProjectPort()
    vm = ProjectViewModel(port=port)
    try:
        vm.selectProject(1)
        port.active_id = 2
        emit_project_context_changed(2)
        assert vm.selectedProjectId == 2
    finally:
        vm.dispose()


def test_apply_workflow_pending_sets_project_scope(qapplication) -> None:
    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel

    class _WfPort:
        def get_active_project_id(self) -> int | None:
            return 42

        def list_workflows(self, *, project_scope_id, include_global: bool):
            assert project_scope_id == 42
            return []

        def list_run_summaries(self, **kwargs):
            return []

        def load_workflow(self, workflow_id: str):
            raise RuntimeError

        def save_workflow(self, definition):
            raise RuntimeError

        def validate_workflow(self, definition):
            raise RuntimeError

        def start_run(self, workflow_id: str, params: dict) -> str:
            return ""

        def get_run(self, run_id: str):
            raise RuntimeError

        def start_run_from_previous(self, run_id: str, initial_input_override=None):
            raise RuntimeError

    wf = WorkflowStudioViewModel(port=_WfPort())
    try:
        wf.applyShellPendingContextJson('{"workflow_ops_scope":"project"}')
        assert wf._list_project_scope_id == 42
    finally:
        wf.dispose()


def test_chat_apply_pending_selects_session(qapplication) -> None:
    from app.ui_contracts.workspaces.chat import ChatListEntry
    from app.ui_runtime.qml.chat.chat_qml_viewmodel import ChatQmlViewModel
    from tests.qml_chat.test_chat_viewmodel import VmTestPort

    port = VmTestPort()
    port._entries = [ChatListEntry(chat_id=7, title="P")]
    port._rows[7] = []
    vm = ChatQmlViewModel(port, schedule_coro=lambda c: None)
    vm.applyShellPendingContextJson('{"chat_id":7}')
    assert vm.activeChatId == 7
