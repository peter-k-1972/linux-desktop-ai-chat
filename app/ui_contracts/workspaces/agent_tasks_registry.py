"""
Agent Tasks — Registry-Liste im Betrieb-Tab (Qt-frei).

Slice 1: Read-only Agentenliste inkl. Issue-Hinweis aus Operations-Summaries.
Slice 2: Selection-/Operations-Detail (Summary/Issues) ohne AgentProfile in Contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

AgentTasksRegistryLoadPhase = Literal["loading", "ready", "no_project", "empty", "error"]

AgentTasksSelectionPhase = Literal["idle", "ready", "error"]


@dataclass(frozen=True, slots=True)
class AgentRegistryRowDto:
    """Eine Zeile in der Registry-Liste (Anzeigetext + stabile agent_id für Auswahl)."""

    agent_id: str
    list_item_text: str


@dataclass(frozen=True, slots=True)
class AgentTasksRegistryViewState:
    """Zustand der Agenten-Registry-Liste."""

    phase: AgentTasksRegistryLoadPhase
    rows: tuple[AgentRegistryRowDto, ...] = ()
    error: SettingsErrorInfo | None = None
    empty_hint: str | None = None


@dataclass(frozen=True, slots=True)
class LoadAgentTasksRegistryCommand:
    """Registry für ``project_id`` neu laden; ``None`` = kein aktives Projekt."""

    project_id: int | None


@dataclass(frozen=True, slots=True)
class AgentTasksOperationsIssueDto:
    """Hinweis aus Operations-Read (Support-Sicht)."""

    code: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class AgentTasksOperationsSummaryDto:
    """Lesendes Agent-Operations-Summary für die Betrieb-Detailspalte."""

    agent_id: str
    slug: str
    display_name: str
    status: str
    assigned_model: str
    model_role: str
    cloud_allowed: bool
    last_activity_at: str | None
    last_activity_source: str
    issues: tuple[AgentTasksOperationsIssueDto, ...] = ()
    workflow_definition_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AgentTasksSelectionViewState:
    """Zustand der Operations-Detailspalte nach Agentenauswahl."""

    phase: AgentTasksSelectionPhase
    summary: AgentTasksOperationsSummaryDto | None = None
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class LoadAgentTaskSelectionCommand:
    """Detail/Summary für ``agent_id`` unter ``project_id`` laden.

    Leere ``agent_id`` → ``phase=idle`` (keine Auswahl).
    """

    agent_id: str
    project_id: int | None


def agent_tasks_registry_loading_state() -> AgentTasksRegistryViewState:
    return AgentTasksRegistryViewState(phase="loading")


def agent_tasks_selection_idle_state() -> AgentTasksSelectionViewState:
    return AgentTasksSelectionViewState(phase="idle")
