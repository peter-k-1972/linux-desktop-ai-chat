"""
Projects Slice 1 — Qt-freie ViewStates, Commands und Event-Payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

ProjectsLoadStatus = Literal["idle", "loading", "ready", "empty", "error"]


@dataclass(slots=True)
class SubscriptionHandle:
    """Kleiner Disposable-Handle für Host-/Kontext-Subscriptions."""

    _dispose: Callable[[], None] | None = None

    def dispose(self) -> None:
        if self._dispose is None:
            return
        cb = self._dispose
        self._dispose = None
        cb()


class ProjectsPortError(Exception):
    """Port-/Adapterfehler für Projects Slice 1."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool
    message: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectListItem:
    project_id: int
    display_name: str
    secondary_text: str
    lifecycle_label: str
    status_label: str
    last_activity_label: str
    is_active: bool
    is_selected: bool
    customer_name: str | None = None
    internal_code: str | None = None
    lifecycle_code: str | None = None
    status_code: str | None = None
    tooltip_text: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectListLoadResult:
    items: tuple[ProjectListItem, ...]
    empty_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectCoreView:
    project_id: int
    name: str
    description_display: str
    lifecycle_label: str
    status_label: str
    default_context_policy_label: str
    customer_name: str | None = None
    external_reference: str | None = None
    internal_code: str | None = None
    planned_start_label: str | None = None
    planned_end_label: str | None = None
    updated_at_label: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectStatsView:
    workflow_count: int
    chat_count: int
    agent_count: int
    file_count: int
    prompt_count: int | None = None
    source_count: int | None = None


@dataclass(frozen=True, slots=True)
class ProjectMonitoringView:
    summary_lines: tuple[str, ...]
    has_data: bool
    headline: str | None = None
    status_tone: str | None = None
    fallback_text: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectActivityChatItem:
    chat_id: int
    title: str
    updated_at_label: str
    topic_name: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectActivityPromptItem:
    prompt_id: int
    title: str
    updated_at_label: str
    scope_label: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectActivitySourceItem:
    source_path: str
    display_name: str
    status_label: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectActivityView:
    recent_chats: tuple[ProjectActivityChatItem, ...] = field(default_factory=tuple)
    recent_prompts: tuple[ProjectActivityPromptItem, ...] = field(default_factory=tuple)
    recent_sources: tuple[ProjectActivitySourceItem, ...] = field(default_factory=tuple)
    has_any_activity: bool = False
    empty_message: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectControllingView:
    budget_label: str | None
    effort_label: str | None
    next_milestone_label: str
    milestone_counts_label: str
    upcoming_milestone_lines: tuple[str, ...] = field(default_factory=tuple)
    has_budget: bool | None = None
    has_effort_estimate: bool | None = None
    warning_message: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectOverviewState:
    project_id: int
    core: ProjectCoreView
    stats: ProjectStatsView
    monitoring: ProjectMonitoringView
    activity: ProjectActivityView
    controlling: ProjectControllingView
    can_set_active: bool
    is_active_project: bool
    empty_reason: str | None = None
    warning_message: str | None = None
    info_message: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectInspectorState:
    project_id: int
    title: str
    status_label: str
    lifecycle_label: str
    context_policy_caption: str
    context_rules_narrative: str
    description_display: str | None = None
    customer_name: str | None = None
    internal_code: str | None = None
    external_reference: str | None = None
    updated_at_label: str | None = None


@dataclass(frozen=True, slots=True)
class ActiveProjectSnapshot:
    active_project_id: int | None
    is_any_project_active: bool
    active_project_name: str | None = None
    active_project_lifecycle_label: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectSelectionChangedPayload:
    selected_project_id: int | None
    selected_project_name: str | None = None
    selection_source: str | None = None


@dataclass(frozen=True, slots=True)
class ActiveProjectChangedPayload:
    active_project_id: int | None
    is_any_project_active: bool
    active_project_name: str | None = None
    change_source: str | None = None


__all__ = [
    "ActiveProjectChangedPayload",
    "ActiveProjectSnapshot",
    "CommandResult",
    "ProjectActivityChatItem",
    "ProjectActivityPromptItem",
    "ProjectActivitySourceItem",
    "ProjectActivityView",
    "ProjectControllingView",
    "ProjectCoreView",
    "ProjectInspectorState",
    "ProjectListItem",
    "ProjectListLoadResult",
    "ProjectMonitoringView",
    "ProjectOverviewState",
    "ProjectSelectionChangedPayload",
    "ProjectsLoadStatus",
    "ProjectsPortError",
    "ProjectStatsView",
    "SubscriptionHandle",
]
