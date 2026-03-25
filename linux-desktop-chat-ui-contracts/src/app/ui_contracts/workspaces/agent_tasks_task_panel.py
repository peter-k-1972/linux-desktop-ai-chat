"""
Agent Tasks — Task-Panel Lesepfad (Slice 4, nur Read; keine Mutation).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AgentTaskPanelPhase = Literal["loading", "ready", "error"]


@dataclass(frozen=True, slots=True)
class AgentTaskPanelDto:
    agent_id: str
    task_count: int
    recent_tasks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AgentTaskPanelState:
    phase: AgentTaskPanelPhase
    panel: AgentTaskPanelDto | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class LoadAgentTaskPanelCommand:
    agent_id: str
    project_id: int | None = None


def agent_task_panel_loading_state() -> AgentTaskPanelState:
    return AgentTaskPanelState(phase="loading", panel=None, error_message=None)
