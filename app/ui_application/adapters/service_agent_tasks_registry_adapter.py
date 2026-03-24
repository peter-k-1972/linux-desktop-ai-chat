"""
Adapter: AgentService + AgentOperationsReadService → Registry-View (Slice 1) + Selection-Detail (Slice 2).

Slice 2b: Ein konsolidierter ``last_registry_snapshot`` nach ``load_registry_view`` (Agents, Profiles,
Summaries) — ersetzt die früheren drei Sidecar-Listen/Dicts. Bei Fehler oder ``no_project`` wird der
Snapshot auf ``None`` gesetzt (nach initialem Clear).

``load_agent_task_selection_detail`` nutzt bei Treffer ``snapshot.summaries_by_id`` statt separater
Summary-Map; bei Fehlern ``phase=error``.

Slice 3: ``load_agent_tasks_inspector_state`` liefert Operations-Texte für den Inspector (Snapshot
oder ``get_summary`` via ``get_agent_operations_read_service``).

Kein zweites Batching in den Services — Aufrufe entsprechen ``_refresh_agents``/``refresh`` Legacy.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.qa.operations_models import AgentOperationsSummary
from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorReadDto
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentRegistryRowDto,
    AgentTasksOperationsIssueDto,
    AgentTasksOperationsSummaryDto,
    AgentTasksRegistryViewState,
    AgentTasksSelectionViewState,
    LoadAgentTaskSelectionCommand,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelDto,
    LoadAgentTaskPanelCommand,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

logger = logging.getLogger(__name__)


@dataclass
class AgentTasksRegistrySnapshot:
    """Letzter erfolgreich geladener Registry-Stand (Sidecar zum Port, nicht im Protocol)."""

    agents: list
    profiles_by_id: dict
    summaries_by_id: dict


def _operations_summary_to_dto(s: AgentOperationsSummary) -> AgentTasksOperationsSummaryDto:
    issues = tuple(
        AgentTasksOperationsIssueDto(
            code=str(getattr(i, "code", "")),
            severity=str(getattr(i, "severity", "")),
            message=str(getattr(i, "message", "")),
        )
        for i in (s.issues or [])
    )
    wf = tuple(str(x) for x in (s.workflow_definition_ids or []) if x is not None)
    return AgentTasksOperationsSummaryDto(
        agent_id=s.agent_id,
        slug=s.slug or "",
        display_name=s.display_name or "",
        status=s.status or "",
        assigned_model=s.assigned_model or "",
        model_role=s.model_role or "",
        cloud_allowed=bool(s.cloud_allowed),
        last_activity_at=s.last_activity_at,
        last_activity_source=s.last_activity_source or "none",
        issues=issues,
        workflow_definition_ids=wf,
    )


def _label_for_profile(
    profile: Any,
    summaries_by_id: dict[str, Any],
) -> str:
    label = f"{profile.effective_display_name}"
    if profile.role:
        label += f" · {profile.role}"
    st = (profile.status or "").strip()
    if st:
        label += f"\n  Status: {st}"
    if profile.assigned_model:
        label += f"\n  Modell: {profile.assigned_model}"
    if profile.id:
        s = summaries_by_id.get(profile.id)
        if s and getattr(s, "issues", None):
            label += f"\n  ⚠ {len(s.issues)} Hinweis(e)"
    return label


def _operations_summary_to_inspector_read_dto(s: AgentOperationsSummary) -> AgentTasksInspectorReadDto:
    n_issues = len(s.issues or [])
    issues_hint = f"{n_issues} Hinweis(e)" if n_issues else "Keine Hinweise"
    act = s.last_activity_at or "—"
    src = s.last_activity_source or "none"
    sec1 = f"Betrieb: {s.display_name or s.slug or s.agent_id}\nStatus: {s.status or '—'}"
    sec2 = (
        f"Zugewiesenes Modell: {s.assigned_model or '—'}\n"
        f"Modell-Rolle: {s.model_role or '—'}\n"
        f"{issues_hint}\n"
        f"Letzte Aktivität ({src}): {act}"
    )
    sec3 = f"Cloud erlaubt: {'ja' if s.cloud_allowed else 'nein'}"
    if s.workflow_definition_ids:
        sec3 += f"\nWorkflow-Definitionen (Knoten): {len(s.workflow_definition_ids)}"
    return AgentTasksInspectorReadDto(
        operations_agent_status=sec1,
        operations_task_context=sec2,
        operations_tool_model=sec3,
    )


class ServiceAgentTasksRegistryAdapter:
    """Delegiert an ``get_agent_service()`` und ``get_agent_operations_read_service()``."""

    def __init__(self) -> None:
        self.last_registry_snapshot: AgentTasksRegistrySnapshot | None = None

    def _clear_sidecar(self) -> None:
        self.last_registry_snapshot = None

    def load_registry_view(self, project_id: int | None) -> AgentTasksRegistryViewState:
        self._clear_sidecar()
        if project_id is None:
            return AgentTasksRegistryViewState(phase="no_project")
        try:
            from app.services.agent_operations_read_service import get_agent_operations_read_service
            from app.services.agent_service import get_agent_service

            service = get_agent_service()
            agents = service.list_agents_for_project(
                project_id,
                department=None,
                status=None,
                filter_text="",
            )
            summaries: list = []
            try:
                summaries = get_agent_operations_read_service().list_summaries(project_id)
            except Exception:
                summaries = []
            summaries_by_id = {s.agent_id: s for s in summaries if getattr(s, "agent_id", None)}
            profiles_by_id = {p.id: p for p in agents if getattr(p, "id", None)}
            self.last_registry_snapshot = AgentTasksRegistrySnapshot(
                agents=list(agents),
                profiles_by_id=dict(profiles_by_id),
                summaries_by_id=dict(summaries_by_id),
            )
            if not agents:
                return AgentTasksRegistryViewState(
                    phase="empty",
                    empty_hint="Keine Agenten – Seed ausführen?",
                )
            rows = tuple(
                AgentRegistryRowDto(
                    agent_id=(p.id or "").strip(),
                    list_item_text=_label_for_profile(p, summaries_by_id),
                )
                for p in agents
            )
            return AgentTasksRegistryViewState(phase="ready", rows=rows)
        except Exception as exc:
            logger.warning("Agent-Registry laden fehlgeschlagen: %s", exc, exc_info=True)
            self._clear_sidecar()
            return AgentTasksRegistryViewState(
                phase="error",
                error=SettingsErrorInfo(
                    code="load_agent_registry_failed",
                    message="Agenten konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )

    def load_agent_task_selection_detail(
        self,
        command: LoadAgentTaskSelectionCommand,
    ) -> AgentTasksSelectionViewState:
        aid = (command.agent_id or "").strip()
        if not aid:
            return AgentTasksSelectionViewState(phase="idle")
        snapshot = self.last_registry_snapshot
        cached = snapshot.summaries_by_id.get(aid) if snapshot else None
        if cached is not None and isinstance(cached, AgentOperationsSummary):
            return AgentTasksSelectionViewState(
                phase="ready",
                summary=_operations_summary_to_dto(cached),
            )
        if command.project_id is None:
            return AgentTasksSelectionViewState(phase="ready", summary=None)
        try:
            from app.services.agent_operations_read_service import get_agent_operations_read_service

            raw = get_agent_operations_read_service().get_summary(aid, command.project_id)
        except Exception as exc:
            logger.warning("Agent-Operations-Summary laden fehlgeschlagen: %s", exc, exc_info=True)
            return AgentTasksSelectionViewState(
                phase="error",
                error=SettingsErrorInfo(
                    code="load_agent_operations_summary_failed",
                    message="Operations-Details konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )
        if raw is None:
            return AgentTasksSelectionViewState(phase="ready", summary=None)
        if isinstance(raw, AgentOperationsSummary):
            return AgentTasksSelectionViewState(
                phase="ready",
                summary=_operations_summary_to_dto(raw),
            )
        return AgentTasksSelectionViewState(phase="ready", summary=None)

    def load_agent_tasks_inspector_state(
        self,
        agent_id: str,
        project_id: int | None,
    ) -> AgentTasksInspectorReadDto:
        aid = (agent_id or "").strip()
        if not aid:
            return AgentTasksInspectorReadDto()
        if project_id is None:
            return AgentTasksInspectorReadDto(
                operations_task_context="Kein aktives Projekt — Operations-Kontext nicht verfügbar.",
            )
        snapshot = self.last_registry_snapshot
        cached = snapshot.summaries_by_id.get(aid) if snapshot else None
        if cached is not None and isinstance(cached, AgentOperationsSummary):
            return _operations_summary_to_inspector_read_dto(cached)
        try:
            from app.services.agent_operations_read_service import get_agent_operations_read_service

            raw = get_agent_operations_read_service().get_summary(aid, project_id)
        except Exception as exc:
            logger.warning("Agent-Inspector-Operations-Read fehlgeschlagen: %s", exc, exc_info=True)
            return AgentTasksInspectorReadDto(
                load_error=SettingsErrorInfo(
                    code="load_agent_tasks_inspector_read_failed",
                    message="Inspector-Operationsdaten konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )
        if raw is None or not isinstance(raw, AgentOperationsSummary):
            return AgentTasksInspectorReadDto(
                operations_task_context="Kein Operations-Summary für diesen Agenten im Projekt.",
            )
        return _operations_summary_to_inspector_read_dto(raw)

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        aid = (command.agent_id or "").strip()
        if not aid:
            return AgentTaskPanelDto(agent_id="", task_count=0, recent_tasks=())
        snapshot = self.last_registry_snapshot
        display = ""
        if snapshot and aid in snapshot.profiles_by_id:
            prof = snapshot.profiles_by_id[aid]
            display = (getattr(prof, "effective_display_name", None) or "").strip()
        try:
            from app.debug.debug_store import get_debug_store

            tasks = list(get_debug_store().get_active_tasks())
        except Exception:
            tasks = []
        matched: list = []
        for t in tasks:
            an = (getattr(t, "agent_name", None) or "").strip()
            if display and an == display:
                matched.append(t)
            elif not display and aid and aid in (getattr(t, "description", None) or ""):
                matched.append(t)

        def _sort_key(t: object) -> float:
            c = getattr(t, "completed_at", None) or getattr(t, "created_at", None)
            return c.timestamp() if c and hasattr(c, "timestamp") else 0.0

        matched.sort(key=_sort_key, reverse=True)
        recent = tuple(
            f"[{getattr(t, 'status', '')}] {(getattr(t, 'description', None) or '')[:120]}"
            for t in matched[:8]
        )
        return AgentTaskPanelDto(
            agent_id=aid,
            task_count=len(matched),
            recent_tasks=recent,
        )
