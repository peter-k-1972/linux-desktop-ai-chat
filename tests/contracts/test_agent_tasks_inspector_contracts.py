"""Agent Tasks Inspector (Slice 3) — Contracts."""

from __future__ import annotations

from app.ui_contracts.workspaces.agent_tasks_inspector import (
    INSPECTOR_SECTION_SEP,
    AgentTasksInspectorPatch,
    AgentTasksInspectorReadDto,
    AgentTasksInspectorState,
    LoadAgentTasksInspectorCommand,
    agent_tasks_inspector_idle_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_inspector_section_sep_distinct() -> None:
    assert "\n" not in INSPECTOR_SECTION_SEP


def test_load_command() -> None:
    c = LoadAgentTasksInspectorCommand("a1", 1, False, "t1", "t2", "t3")
    assert c.agent_id == "a1"
    assert c.task_section_2 == "t2"


def test_state_and_idle() -> None:
    st = agent_tasks_inspector_idle_state()
    assert st.phase == "idle"
    s2 = AgentTasksInspectorState(phase="ready", agent_id="x", sending=True, last_result_text="a")
    assert s2.sending is True


def test_read_dto_error() -> None:
    err = SettingsErrorInfo(code="c", message="m")
    dto = AgentTasksInspectorReadDto(load_error=err)
    assert dto.load_error == err


def test_patch_optional() -> None:
    p = AgentTasksInspectorPatch(sending=False)
    assert p.last_result_text is None
