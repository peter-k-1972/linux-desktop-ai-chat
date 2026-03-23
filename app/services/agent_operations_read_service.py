"""
Agent Operations Read – R2 supportorientierte Lesesicht.

Keine Task-Ausführung, kein CRUD, keine GUI.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.metrics.metrics_store import MetricsStore, get_metrics_store
from app.qa.operations_models import AgentOperationsIssue, AgentOperationsSummary
from app.services.infrastructure_snapshot import fetch_ollama_tag_names
from app.services.workflow_service import WorkflowService, get_workflow_service
from app.workflows.queries.agent_workflow_definitions import list_workflow_ids_referencing_agent


def _app_db_path() -> str:
    try:
        from app.services.infrastructure import get_infrastructure

        return getattr(get_infrastructure().database, "db_path", None) or "chat_history.db"
    except Exception:
        return "chat_history.db"


class AgentOperationsReadService:
    """Baut AgentOperationsSummary aus Profil, Metrics und Workflow-Definitionen."""

    def __init__(
        self,
        metrics_store: Optional[MetricsStore] = None,
        workflow_service_getter: Optional[Callable[[], WorkflowService]] = None,
    ) -> None:
        self._metrics_override = metrics_store
        self._workflow_service_getter = workflow_service_getter or get_workflow_service

    def _metrics_store(self) -> MetricsStore:
        if self._metrics_override is not None:
            return self._metrics_override
        return get_metrics_store(_app_db_path())

    def _last_metrics_activity(self, agent_id: str) -> tuple[Optional[str], str]:
        ts = self._metrics_store().get_latest_event_timestamp(agent_id)
        if ts is None:
            return None, "none"
        if ts.tzinfo is None:
            from datetime import timezone

            ts = ts.replace(tzinfo=timezone.utc)
        return ts.isoformat(), "metrics"

    def _collect_issues(
        self,
        profile: AgentProfile,
        ollama_tag_names: Optional[List[str]],
    ) -> List[AgentOperationsIssue]:
        issues: List[AgentOperationsIssue] = []
        st = (profile.status or "").strip().lower()
        if st == AgentStatus.INACTIVE.value:
            issues.append(
                AgentOperationsIssue(
                    "AGENT_INACTIVE",
                    "warning",
                    "Agent ist deaktiviert (status=inactive).",
                )
            )
        if st == AgentStatus.ARCHIVED.value:
            issues.append(
                AgentOperationsIssue(
                    "AGENT_ARCHIVED",
                    "warning",
                    "Agent ist archiviert.",
                )
            )
        model = (profile.assigned_model or "").strip()
        if not model:
            issues.append(
                AgentOperationsIssue(
                    "NO_ASSIGNED_MODEL",
                    "warning",
                    "Kein zugewiesenes Modell (assigned_model leer).",
                )
            )
        elif ollama_tag_names is not None:
            if model not in ollama_tag_names:
                issues.append(
                    AgentOperationsIssue(
                        "MODEL_NOT_IN_OLLAMA_TAGS",
                        "warning",
                        f"Modell {model!r} erscheint nicht in Ollama /api/tags.",
                    )
                )
        return issues

    def _workflow_ids_for_agent(
        self,
        definitions: List,
        profile: AgentProfile,
    ) -> List[str]:
        return list_workflow_ids_referencing_agent(
            definitions,
            agent_id=(profile.id or "").strip() or None,
            slug=(profile.slug or "").strip() or None,
        )

    def list_summaries(self, project_id: Optional[int]) -> List[AgentOperationsSummary]:
        from app.services.agent_service import get_agent_service

        agents = get_agent_service().list_agents_for_project(
            project_id,
            department=None,
            status=None,
            filter_text="",
        )
        ollama_names, _detail = fetch_ollama_tag_names()
        wf_svc = self._workflow_service_getter()
        try:
            definitions = wf_svc.list_workflows(
                project_scope_id=project_id,
                include_global=True,
            )
        except Exception:
            definitions = []

        summaries: List[AgentOperationsSummary] = []
        for p in agents:
            if not p.id:
                continue
            summaries.append(self._build_summary_for_profile(p, ollama_names, definitions))
        return summaries

    def _build_summary_for_profile(
        self,
        profile: AgentProfile,
        ollama_names: Optional[List[str]],
        definitions: List,
    ) -> AgentOperationsSummary:
        assert profile.id
        last_at, src = self._last_metrics_activity(profile.id)
        issues = self._collect_issues(profile, ollama_names)
        wf_ids = self._workflow_ids_for_agent(definitions, profile)
        return AgentOperationsSummary(
            agent_id=profile.id,
            slug=(profile.slug or "").strip(),
            display_name=profile.effective_display_name,
            status=(profile.status or "").strip(),
            assigned_model=(profile.assigned_model or "").strip(),
            model_role=(profile.assigned_model_role or "").strip(),
            cloud_allowed=bool(profile.cloud_allowed),
            last_activity_at=last_at,
            last_activity_source=src,
            issues=issues,
            workflow_definition_ids=wf_ids,
        )

    def get_summary(
        self,
        agent_id: str,
        project_id: Optional[int],
    ) -> Optional[AgentOperationsSummary]:
        from app.services.agent_service import get_agent_service

        facade = get_agent_service()
        profile = facade.get_agent(agent_id)
        if not profile or not profile.id:
            return None
        visible_ids = {
            p.id for p in facade.list_agents_for_project(project_id, status=None, filter_text="") if p.id
        }
        if profile.id not in visible_ids:
            return None
        ollama_names, _detail = fetch_ollama_tag_names()
        wf_svc = self._workflow_service_getter()
        try:
            definitions = wf_svc.list_workflows(
                project_scope_id=project_id,
                include_global=True,
            )
        except Exception:
            definitions = []
        return self._build_summary_for_profile(profile, ollama_names, definitions)


_read_service: Optional[AgentOperationsReadService] = None


def get_agent_operations_read_service() -> AgentOperationsReadService:
    global _read_service
    if _read_service is None:
        _read_service = AgentOperationsReadService()
    return _read_service


def reset_agent_operations_read_service() -> None:
    """Tests: Singleton zurücksetzen."""
    global _read_service
    _read_service = None
