"""
Adapter: bestehende Services / Projektkontext → ProjectsOverviewReadPort.

Nur Delegation und triviale Mapping-Schritte für Projects Slice 1.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from app.core.context.project_context_events import (
    subscribe_project_context_events,
    unsubscribe_project_context_events,
)
from app.projects.controlling import (
    format_budget_display,
    format_effort_display,
    format_milestone_compact_counts,
    format_next_milestone_line,
    milestone_summary,
)
from app.projects.lifecycle import lifecycle_label_de
from app.projects.models import (
    format_context_rules_narrative,
    format_default_context_policy_caption,
)
from app.projects.monitoring_display import monitoring_overview_lines
from app.services.project_service import get_project_service
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ActiveProjectSnapshot,
    ProjectActivityChatItem,
    ProjectActivityPromptItem,
    ProjectActivitySourceItem,
    ProjectActivityView,
    ProjectControllingView,
    ProjectCoreView,
    ProjectInspectorState,
    ProjectListItem,
    ProjectListLoadResult,
    ProjectMonitoringView,
    ProjectOverviewState,
    ProjectStatsView,
    SubscriptionHandle,
)


def _fmt_last_access(ts: str | None) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(ts) if ts else "—"


def _fmt_overview_timestamp(ts: str | None) -> str | None:
    if ts is None or not str(ts).strip():
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        s = str(ts).strip()
        return s or None


def _recency_key(project: dict[str, Any]) -> datetime:
    for key in ("updated_at", "created_at"):
        raw = project.get(key)
        if not raw:
            continue
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except Exception:
            continue
    return datetime.min


def _project_secondary_text(project: dict[str, Any]) -> str:
    return ((project.get("internal_code") or "").strip() or (project.get("customer_name") or "").strip())


def _status_label(project: dict[str, Any]) -> str:
    return str((project.get("status") or "active")).strip() or "active"


def _planned_date_label(raw: object) -> str | None:
    s = str(raw).strip() if raw is not None else ""
    return s or None


def _map_project_list_item(
    project: dict[str, Any],
    *,
    active_project_id: int | None,
    selected_project_id: int | None,
) -> ProjectListItem:
    pid = int(project.get("project_id") or 0)
    name = (project.get("name") or "Projekt").strip()
    secondary = _project_secondary_text(project)
    lifecycle_code = str(project.get("lifecycle_status") or "").strip().lower() or None
    status_code = str(project.get("status") or "").strip() or None
    tooltip = name if not secondary else f"{name} · {secondary}"
    return ProjectListItem(
        project_id=pid,
        display_name=name,
        secondary_text=secondary,
        lifecycle_label=lifecycle_label_de(lifecycle_code),
        status_label=_status_label(project),
        last_activity_label=_fmt_last_access(project.get("updated_at") or project.get("created_at")),
        is_active=active_project_id == pid,
        is_selected=selected_project_id == pid,
        customer_name=((project.get("customer_name") or "").strip() or None),
        internal_code=((project.get("internal_code") or "").strip() or None),
        lifecycle_code=lifecycle_code,
        status_code=status_code,
        tooltip_text=tooltip,
    )


def _map_activity_chats(rows: list[dict[str, Any]]) -> tuple[ProjectActivityChatItem, ...]:
    out: list[ProjectActivityChatItem] = []
    for row in rows:
        cid = row.get("chat_id")
        if cid is None:
            continue
        out.append(
            ProjectActivityChatItem(
                chat_id=int(cid),
                title=((row.get("title") or "Chat").strip() or "Chat"),
                updated_at_label=_fmt_last_access(row.get("updated_at") or row.get("created_at")),
                topic_name=((row.get("topic_name") or "").strip() or None),
            )
        )
    return tuple(out)


def _map_activity_prompts(rows: list[Any]) -> tuple[ProjectActivityPromptItem, ...]:
    out: list[ProjectActivityPromptItem] = []
    for row in rows:
        pid = getattr(row, "id", None)
        if pid is None:
            continue
        updated = getattr(row, "updated_at", None) or getattr(row, "created_at", None)
        updated_label = _fmt_last_access(updated.isoformat() if hasattr(updated, "isoformat") else updated)
        out.append(
            ProjectActivityPromptItem(
                prompt_id=int(pid),
                title=(str(getattr(row, "title", "") or "Prompt").strip() or "Prompt"),
                updated_at_label=updated_label,
                scope_label="Projekt",
            )
        )
    return tuple(out)


def _map_activity_sources(rows: list[dict[str, Any]]) -> tuple[ProjectActivitySourceItem, ...]:
    out: list[ProjectActivitySourceItem] = []
    for row in rows:
        raw_path = row.get("source_path") or row.get("path") or row.get("file_path") or ""
        source_path = str(raw_path).strip()
        if not source_path:
            continue
        out.append(
            ProjectActivitySourceItem(
                source_path=source_path,
                display_name=Path(source_path).name or source_path,
                status_label=(str(row.get("status")).strip() if row.get("status") is not None else None) or None,
            )
        )
    return tuple(out)


class ServiceProjectsOverviewReadAdapter:
    def load_project_list(
        self,
        filter_text: str,
        *,
        active_project_id: int | None = None,
        selected_project_id: int | None = None,
    ) -> ProjectListLoadResult:
        projects = list(get_project_service().list_projects(filter_text or ""))
        projects.sort(key=_recency_key, reverse=True)
        items = tuple(
            _map_project_list_item(
                project,
                active_project_id=active_project_id,
                selected_project_id=selected_project_id,
            )
            for project in projects
        )
        if items:
            return ProjectListLoadResult(items=items, empty_reason=None)
        return ProjectListLoadResult(
            items=(),
            empty_reason="no_filter_match" if (filter_text or "").strip() else "no_projects",
        )

    def load_project_overview(self, project_id: int) -> ProjectOverviewState | None:
        svc = get_project_service()
        project = svc.get_project(int(project_id))
        if not project:
            return None
        pid = int(project["project_id"])
        active_id = svc.get_active_project_id()
        monitoring_snapshot = svc.get_project_monitoring_snapshot(pid)
        activity = svc.get_recent_project_activity(pid, chat_limit=5, prompt_limit=5)
        milestones = svc.list_project_milestones(pid)
        summary = milestone_summary(milestones)
        upcoming_lines = tuple(
            line
            for line in (
                format_next_milestone_line(milestone) for milestone in summary.get("upcoming_three") or []
            )
            if line
        )
        return ProjectOverviewState(
            project_id=pid,
            core=ProjectCoreView(
                project_id=pid,
                name=(project.get("name") or "Projekt").strip() or "Projekt",
                description_display=(project.get("description") or "").strip() or "—",
                lifecycle_label=lifecycle_label_de(project.get("lifecycle_status")),
                status_label=_status_label(project),
                default_context_policy_label=format_default_context_policy_caption(project),
                customer_name=((project.get("customer_name") or "").strip() or None),
                external_reference=((project.get("external_reference") or "").strip() or None),
                internal_code=((project.get("internal_code") or "").strip() or None),
                planned_start_label=_planned_date_label(project.get("planned_start_date")),
                planned_end_label=_planned_date_label(project.get("planned_end_date")),
                updated_at_label=_fmt_overview_timestamp(project.get("updated_at") or project.get("created_at")),
            ),
            stats=ProjectStatsView(
                workflow_count=svc.count_workflows_of_project(pid),
                chat_count=svc.count_chats_of_project(pid),
                agent_count=svc.count_agents_of_project(pid),
                file_count=svc.count_files_of_project(pid),
                prompt_count=svc.count_prompts_of_project(pid),
                source_count=int(monitoring_snapshot.get("source_count") or 0),
            ),
            monitoring=ProjectMonitoringView(
                summary_lines=tuple(monitoring_overview_lines(monitoring_snapshot)),
                has_data=True,
                headline="Betrieb / Monitoring",
            ),
            activity=ProjectActivityView(
                recent_chats=_map_activity_chats(activity.get("recent_chats", [])),
                recent_prompts=_map_activity_prompts(activity.get("recent_prompts", [])),
                recent_sources=_map_activity_sources(activity.get("sources", [])),
                has_any_activity=bool(
                    activity.get("recent_chats") or activity.get("recent_prompts") or activity.get("sources")
                ),
                empty_message="Keine aktuelle Aktivität." if not (
                    activity.get("recent_chats") or activity.get("recent_prompts") or activity.get("sources")
                ) else None,
            ),
            controlling=ProjectControllingView(
                budget_label=format_budget_display(project.get("budget_amount"), project.get("budget_currency")),
                effort_label=format_effort_display(project.get("estimated_effort_hours")),
                next_milestone_label=format_next_milestone_line(summary.get("next_milestone")) or "—",
                milestone_counts_label=format_milestone_compact_counts(
                    int(summary.get("open_count") or 0),
                    int(summary.get("overdue_count") or 0),
                ),
                upcoming_milestone_lines=upcoming_lines,
                has_budget=project.get("budget_amount") is not None,
                has_effort_estimate=project.get("estimated_effort_hours") is not None,
            ),
            can_set_active=active_id != pid,
            is_active_project=active_id == pid,
        )

    def load_project_inspector(self, project_id: int) -> ProjectInspectorState | None:
        svc = get_project_service()
        project = svc.get_project(int(project_id))
        if not project:
            return None
        pid = int(project["project_id"])
        return ProjectInspectorState(
            project_id=pid,
            title=(project.get("name") or "Projekt").strip() or "Projekt",
            status_label=_status_label(project),
            lifecycle_label=lifecycle_label_de(project.get("lifecycle_status")),
            context_policy_caption=format_default_context_policy_caption(project),
            context_rules_narrative=format_context_rules_narrative(project),
            description_display=(project.get("description") or "").strip() or "—",
            customer_name=((project.get("customer_name") or "").strip() or None),
            internal_code=((project.get("internal_code") or "").strip() or None),
            external_reference=((project.get("external_reference") or "").strip() or None),
            updated_at_label=_fmt_overview_timestamp(project.get("updated_at") or project.get("created_at")),
        )

    def load_active_project_snapshot(self) -> ActiveProjectSnapshot:
        svc = get_project_service()
        active = svc.get_active_project()
        active_id = svc.get_active_project_id()
        if not active_id or not isinstance(active, dict):
            return ActiveProjectSnapshot(active_project_id=None, is_any_project_active=False)
        return ActiveProjectSnapshot(
            active_project_id=int(active_id),
            is_any_project_active=True,
            active_project_name=((active.get("name") or "").strip() or None),
            active_project_lifecycle_label=lifecycle_label_de(active.get("lifecycle_status")),
        )

    def subscribe_active_project_changed(
        self,
        listener: Callable[[ActiveProjectChangedPayload], None],
    ) -> SubscriptionHandle:
        def _bridge(payload: dict[str, Any]) -> None:
            pid_raw = payload.get("project_id")
            pid = int(pid_raw) if isinstance(pid_raw, int) else None
            snap = self.load_active_project_snapshot()
            listener(
                ActiveProjectChangedPayload(
                    active_project_id=pid,
                    is_any_project_active=snap.is_any_project_active,
                    active_project_name=snap.active_project_name,
                    change_source="host_event",
                )
            )

        subscribe_project_context_events(_bridge)
        return SubscriptionHandle(lambda: unsubscribe_project_context_events(_bridge))
