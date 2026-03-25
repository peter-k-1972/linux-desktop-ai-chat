"""
Agent Tasks — Inspector-Inhalt (Qt-frei, Slice 3).

Read-Pfad: Operations-Kontext aus Port/Adapter; Task-Zeilen aus Workspace (kein AgentTaskResult im Contract).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.common.errors import SettingsErrorInfo

AgentTasksInspectorPhase = Literal["idle", "ready", "error"]

# Drei Inspector-Abschnitte (Agentenstatus / Task-Kontext / Tool·Model) — serialisiert in ``last_result_text``.
INSPECTOR_SECTION_SEP = "\x1e"


@dataclass(frozen=True, slots=True)
class AgentTasksInspectorReadDto:
    """Read-only Operations-Anteil für den Inspector (Adapter → Presenter)."""

    operations_agent_status: str = ""
    operations_task_context: str = ""
    operations_tool_model: str = ""
    load_error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class AgentTasksInspectorState:
    phase: AgentTasksInspectorPhase
    agent_id: str = ""
    sending: bool = False
    last_result_text: str = ""


@dataclass(frozen=True, slots=True)
class AgentTasksInspectorPatch:
    """Optional Teilupdate (Slice 3: vor allem für spätere Erweiterungen)."""

    sending: bool | None = None
    last_result_text: str | None = None


@dataclass(frozen=True, slots=True)
class LoadAgentTasksInspectorCommand:
    """Inspector neu laden: Operations-Read über Port; Task-Texte aus Workspace."""

    agent_id: str
    project_id: int | None
    sending: bool
    task_section_1: str = ""
    task_section_2: str = ""
    task_section_3: str = ""


def agent_tasks_inspector_idle_state() -> AgentTasksInspectorState:
    return AgentTasksInspectorState(phase="idle")


__all__ = [
    "AgentTasksInspectorPatch",
    "AgentTasksInspectorPhase",
    "AgentTasksInspectorReadDto",
    "AgentTasksInspectorState",
    "INSPECTOR_SECTION_SEP",
    "LoadAgentTasksInspectorCommand",
    "agent_tasks_inspector_idle_state",
]
