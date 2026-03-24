"""
ProjectService – Projekte, Zuordnungen, Statistiken.

Zentrale API für Projekt-Operationen. Nutzt DatabaseManager.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.chat.context_policies import ChatContextPolicy

from app.core.db.database_manager import PROJECT_UPDATE_OMIT
from app.projects.lifecycle import (
    DEFAULT_LIFECYCLE_STATUS,
    normalize_optional_plan_date,
    normalize_optional_text,
    validate_lifecycle_status,
)
from app.projects.milestones import (
    validate_milestone_name,
    validate_milestone_status,
    validate_milestone_target_date,
)
from app.services.infrastructure import get_infrastructure


def _normalize_budget_currency(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip().upper()
    return s if s else None


def _optional_nonneg_float(raw: Any, label: str) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, str) and not str(raw).strip():
        return None
    try:
        v = float(str(raw).strip().replace(",", "."))
    except ValueError as e:
        raise ValueError(f"{label}: ungültige Zahl") from e
    if v < 0:
        raise ValueError(f"{label} darf nicht negativ sein")
    return v


class ProjectService:
    """Service für Projekte: CRUD, Zuordnungen, Statistiken."""

    def __init__(self):
        self._infra = get_infrastructure()

    def list_projects(self, filter_text: str = "") -> List[Dict[str, Any]]:
        """Liste aller Projekte."""
        return self._infra.database.list_projects(filter_text)

    def create_project(
        self,
        name: str,
        description: str = "",
        status: str = "active",
        default_context_policy: Optional[str] = None,
        customer_name: Optional[str] = None,
        external_reference: Optional[str] = None,
        internal_code: Optional[str] = None,
        lifecycle_status: str = DEFAULT_LIFECYCLE_STATUS,
        planned_start_date: Optional[str] = None,
        planned_end_date: Optional[str] = None,
        budget_amount: Any = None,
        budget_currency: Any = None,
        estimated_effort_hours: Any = None,
    ) -> int:
        """Erstellt ein Projekt. Gibt project_id zurück."""
        ls = validate_lifecycle_status(lifecycle_status)
        ps = normalize_optional_plan_date(planned_start_date)
        pe = normalize_optional_plan_date(planned_end_date)
        ba = _optional_nonneg_float(budget_amount, "Budget")
        be = _optional_nonneg_float(estimated_effort_hours, "Aufwandsschätzung (h)")
        bc = _normalize_budget_currency(budget_currency)
        pid = self._infra.database.create_project(
            name,
            description,
            status,
            default_context_policy,
            customer_name=normalize_optional_text(customer_name),
            external_reference=normalize_optional_text(external_reference),
            internal_code=normalize_optional_text(internal_code),
            lifecycle_status=ls,
            planned_start_date=ps,
            planned_end_date=pe,
            budget_amount=ba,
            budget_currency=bc,
            estimated_effort_hours=be,
        )
        try:
            from app.services.audit_service import get_audit_service

            get_audit_service().record_project_created(project_id=pid, name=name)
        except Exception as exc:
            _log.warning("Audit (project_created): %s", exc)
        return pid

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Liefert ein Projekt oder None."""
        return self._infra.database.get_project(project_id)

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        default_context_policy: Optional[str] = None,
        *,
        clear_default_context_policy: bool = False,
        customer_name: Any = PROJECT_UPDATE_OMIT,
        external_reference: Any = PROJECT_UPDATE_OMIT,
        internal_code: Any = PROJECT_UPDATE_OMIT,
        lifecycle_status: Any = PROJECT_UPDATE_OMIT,
        planned_start_date: Any = PROJECT_UPDATE_OMIT,
        planned_end_date: Any = PROJECT_UPDATE_OMIT,
        budget_amount: Any = PROJECT_UPDATE_OMIT,
        budget_currency: Any = PROJECT_UPDATE_OMIT,
        estimated_effort_hours: Any = PROJECT_UPDATE_OMIT,
    ) -> None:
        """Aktualisiert Projektfelder. clear_default_context_policy entfernt die gespeicherte Kontext-Policy."""
        kw: Dict[str, Any] = {}
        if customer_name is not PROJECT_UPDATE_OMIT:
            kw["customer_name"] = normalize_optional_text(customer_name)
        if external_reference is not PROJECT_UPDATE_OMIT:
            kw["external_reference"] = normalize_optional_text(external_reference)
        if internal_code is not PROJECT_UPDATE_OMIT:
            kw["internal_code"] = normalize_optional_text(internal_code)
        if lifecycle_status is not PROJECT_UPDATE_OMIT:
            kw["lifecycle_status"] = validate_lifecycle_status(lifecycle_status)
        if planned_start_date is not PROJECT_UPDATE_OMIT:
            kw["planned_start_date"] = normalize_optional_plan_date(planned_start_date)
        if planned_end_date is not PROJECT_UPDATE_OMIT:
            kw["planned_end_date"] = normalize_optional_plan_date(planned_end_date)
        if budget_amount is not PROJECT_UPDATE_OMIT:
            kw["budget_amount"] = _optional_nonneg_float(budget_amount, "Budget")
        if budget_currency is not PROJECT_UPDATE_OMIT:
            kw["budget_currency"] = _normalize_budget_currency(budget_currency)
        if estimated_effort_hours is not PROJECT_UPDATE_OMIT:
            kw["estimated_effort_hours"] = _optional_nonneg_float(
                estimated_effort_hours, "Aufwandsschätzung (h)"
            )

        updated = self._infra.database.update_project(
            project_id,
            name,
            description,
            status,
            default_context_policy,
            clear_default_context_policy=clear_default_context_policy,
            **kw,
        )
        if not updated:
            return
        try:
            from app.services.audit_service import get_audit_service

            row = self._infra.database.get_project(project_id)
            nh = (row or {}).get("name")
            get_audit_service().record_project_updated(project_id=project_id, name_hint=nh)
        except Exception as exc:
            _log.warning("Audit (project_updated): %s", exc)

    def delete_project(self, project_id: int) -> None:
        """
        Löscht ein Projekt mit definierter Lebenszyklussemantik.

        SQLite (transaktional): siehe ``DatabaseManager.delete_project`` (Chats entkoppeln,
        Topics und project_files-Links entfernen, Prompts/Agents/Workflows globalisieren, Projektzeile löschen).

        Anschließend: RAG-Unterordner ``project_{id}`` best effort entfernen (Fehler nur geloggt).
        War dieses Projekt aktiv, wird der Projektkontext per ``ProjectContextManager`` geleert.
        """
        row = self._infra.database.get_project(project_id)
        deleted_name = (row or {}).get("name") if row else None
        self._infra.database.delete_project(project_id)
        try:
            from app.services.audit_service import get_audit_service

            get_audit_service().record_project_deleted(project_id=project_id, name=deleted_name)
        except Exception as exc:
            _log.warning("Audit (project_deleted): %s", exc)
        try:
            from app.services.knowledge_service import get_knowledge_service

            get_knowledge_service().remove_project_space(project_id)
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning(
                "Knowledge-Raum für project_id=%s konnte nicht entfernt werden: %s",
                project_id,
                exc,
            )
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            pcm = get_project_context_manager()
            if pcm.get_active_project_id() == project_id:
                pcm.set_active_project(None)
        except Exception:
            pass

    def add_chat_to_project(self, project_id: int, chat_id: int) -> None:
        """Ordnet einen Chat einem Projekt zu."""
        self._infra.database.add_chat_to_project(project_id, chat_id)

    def remove_chat_from_project(self, project_id: int, chat_id: int) -> None:
        """Entfernt die Zuordnung Chat–Projekt."""
        self._infra.database.remove_chat_from_project(project_id, chat_id)

    def move_chat_to_project(
        self, chat_id: int, target_project_id: int, topic_id: Optional[int] = None
    ) -> None:
        """
        Verschiebt einen Chat zu einem anderen Projekt.
        Entfernt aus aktuellem Projekt (falls vorhanden) und ordnet dem Zielprojekt zu.
        """
        old_id = self.get_project_of_chat(chat_id)
        if old_id:
            self.remove_chat_from_project(old_id, chat_id)
        self._infra.database.add_chat_to_project(project_id=target_project_id, chat_id=chat_id, topic_id=topic_id)

    def get_project_of_chat(self, chat_id: int) -> Optional[int]:
        """Liefert die project_id des Chats oder None."""
        return self._infra.database.get_project_of_chat(chat_id)

    def get_project_context_policy_for_chat(self, chat_id: int) -> Optional["ChatContextPolicy"]:
        """Liefert die default_context_policy des Projekt-Chats oder None."""
        from app.projects.models import get_default_context_policy

        project_id = self.get_project_of_chat(chat_id)
        if not project_id:
            return None
        project = self.get_project(project_id)
        return get_default_context_policy(project)

    def list_chats_of_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Liste der Chats eines Projekts."""
        return self._infra.database.list_chats_of_project(project_id)

    def get_recent_chats_of_project(self, project_id: int, limit: int = 8) -> List[Dict[str, Any]]:
        """Letzte Chat-Sessions des Projekts (nach letzter Nachricht / Erstellung)."""
        return self._infra.database.get_recent_chats_of_project(project_id, limit)

    def count_chats_of_project(self, project_id: int) -> int:
        """Anzahl Chats eines Projekts."""
        return self._infra.database.count_chats_of_project(project_id)

    def count_files_of_project(self, project_id: int) -> int:
        """Anzahl Dateien eines Projekts."""
        return self._infra.database.count_files_of_project(project_id)

    def list_files_of_project(self, project_id: int, limit: int = 40) -> List[Dict[str, Any]]:
        """Liste verknüpfter Dateien (Metadaten aus ``files``)."""
        return self._infra.database.list_files_of_project(project_id, limit)

    def count_prompts_of_project(self, project_id: int) -> int:
        """Anzahl Prompts eines Projekts."""
        return self._infra.database.count_prompts_of_project(project_id)

    def count_agents_of_project(self, project_id: int) -> int:
        """Anzahl dem Projekt zugeordneter Agentenprofile."""
        return self._infra.database.count_agents_of_project(project_id)

    def count_workflows_of_project(self, project_id: int) -> int:
        """Anzahl Workflows, die ausschließlich diesem Projekt zugeordnet sind (nicht global)."""
        try:
            from app.services.workflow_service import get_workflow_service

            return len(
                get_workflow_service().list_workflows(
                    project_scope_id=project_id,
                    include_global=False,
                )
            )
        except Exception:
            return 0

    # --- Aktiver Projektkontext (lesen/schreiben über ProjectContextManager) ---

    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Liefert das aktuell aktive Projekt oder None (autoritativ: ProjectContextManager)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            return get_project_context_manager().get_active_project()
        except Exception:
            return None

    def get_active_project_id(self) -> Optional[int]:
        """Liefert die ID des aktiven Projekts oder None (autoritativ: ProjectContextManager)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            return get_project_context_manager().get_active_project_id()
        except Exception:
            return None

    def set_active_project(self, project_id: Optional[int] = None, project: Optional[Dict[str, Any]] = None) -> None:
        """Setzt das aktive Projekt – delegiert an ProjectContextManager (inkl. Event/Sync)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            pcm = get_project_context_manager()
            if project_id is None and project is None:
                pcm.set_active_project(None)
                return
            pid = project_id
            if pid is None and project is not None:
                pid = project.get("project_id")
            pcm.set_active_project(pid)
        except Exception:
            pass

    def clear_active_project(self) -> None:
        """Entfernt den aktiven Projektkontext (delegiert an ProjectContextManager)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            get_project_context_manager().set_active_project(None)
        except Exception:
            pass

    def get_project_sources(self, project_id: int) -> List[Dict[str, Any]]:
        """Liefert Knowledge-Quellen eines Projekts (über KnowledgeService)."""
        try:
            from app.services.knowledge_service import get_knowledge_service
            space = f"project_{project_id}"
            return get_knowledge_service().list_sources(space)
        except Exception:
            return []

    def get_project_prompts(self, project_id: int) -> List[Any]:
        """Liefert Prompts eines Projekts (über PromptService)."""
        try:
            from app.prompts.prompt_service import get_prompt_service
            return get_prompt_service().list_for_project(project_id)
        except Exception:
            return []

    def get_project_summary(self, project_id: int) -> Dict[str, Any]:
        """Zusammenfassung eines Projekts: Metadaten + Kennzahlen."""
        proj = self.get_project(project_id)
        if not proj:
            return {}
        return {
            **proj,
            "chat_count": self.count_chats_of_project(project_id),
            "source_count": len(self.get_project_sources(project_id)),
            "prompt_count": self.count_prompts_of_project(project_id),
        }

    def get_project_monitoring_snapshot(self, project_id: int) -> Dict[str, Any]:
        """
        Operatives Monitoring aus vorhandenen Daten (Chats, Workflow-Runs, Quellenliste).
        Keine persistierten Monitoring-Felder, keine Scores.
        """
        db = self._infra.database
        last_activity_at = db.get_project_last_activity(project_id)
        message_count_7d = db.count_project_messages_in_days(project_id, 7)
        message_count_30d = db.count_project_messages_in_days(project_id, 30)
        active_chats_30d = db.count_active_project_chats_in_days(project_id, 30)
        sources = self.get_project_sources(project_id)
        source_count = len(sources)

        wf_part: Dict[str, Any] = {
            "last_workflow_run_at": None,
            "last_workflow_run_status": None,
            "failed_workflow_runs_30d": 0,
        }
        try:
            from app.services.workflow_service import get_workflow_service

            wf_part = get_workflow_service().get_project_workflow_monitoring_snapshot(project_id)
        except Exception:
            pass

        from app.projects.monitoring_display import knowledge_sources_line

        return {
            "last_activity_at": last_activity_at,
            "message_count_7d": int(message_count_7d),
            "message_count_30d": int(message_count_30d),
            "active_chats_30d": int(active_chats_30d),
            "last_workflow_run_at": wf_part.get("last_workflow_run_at"),
            "last_workflow_run_status": wf_part.get("last_workflow_run_status"),
            "failed_workflow_runs_30d": int(wf_part.get("failed_workflow_runs_30d") or 0),
            "source_count": int(source_count),
            "knowledge_hint": knowledge_sources_line(source_count),
        }

    def get_recent_project_activity(
        self,
        project_id: int,
        chat_limit: int = 5,
        prompt_limit: int = 5,
    ) -> Dict[str, Any]:
        """Letzte Aktivität eines Projekts: Chats, Prompts, Quellen."""
        chats = []
        try:
            chats = self._infra.database.get_recent_chats_of_project(project_id, chat_limit)
        except Exception:
            pass
        prompts = []
        try:
            from app.prompts.prompt_service import get_prompt_service
            from datetime import datetime
            all_prompts = get_prompt_service().list_project_prompts(project_id)
            prompts = sorted(
                all_prompts,
                key=lambda p: getattr(p, "updated_at", None) or getattr(p, "created_at", None) or datetime.min,
                reverse=True,
            )[:prompt_limit]
        except Exception:
            pass
        sources = self.get_project_sources(project_id)
        return {
            "recent_chats": chats,
            "recent_prompts": prompts,
            "sources": sources[:5],
        }

    def list_project_milestones(self, project_id: int) -> List[Dict[str, Any]]:
        return self._infra.database.list_project_milestones(project_id)

    def get_project_milestone(self, milestone_id: int) -> Optional[Dict[str, Any]]:
        return self._infra.database.get_project_milestone(milestone_id)

    def create_project_milestone(
        self,
        project_id: int,
        name: str,
        target_date: str,
        status: str = "open",
        sort_order: int = 0,
        notes: Optional[str] = None,
    ) -> int:
        nm = validate_milestone_name(name)
        td = validate_milestone_target_date(target_date)
        st = validate_milestone_status(status)
        so = int(sort_order)
        nt = normalize_optional_text(notes)
        return self._infra.database.create_project_milestone(
            project_id, nm, td, st, so, nt
        )

    def update_project_milestone(
        self,
        milestone_id: int,
        *,
        project_id: int,
        name: str,
        target_date: str,
        status: str,
        sort_order: int,
        notes: Optional[str] = None,
    ) -> None:
        row = self._infra.database.get_project_milestone(milestone_id)
        if not row or int(row.get("project_id") or 0) != int(project_id):
            raise ValueError("Meilenstein nicht gefunden oder falsches Projekt")
        nm = validate_milestone_name(name)
        td = validate_milestone_target_date(target_date)
        st = validate_milestone_status(status)
        so = int(sort_order)
        nt = normalize_optional_text(notes)
        self._infra.database.update_project_milestone(
            milestone_id, nm, td, st, so, nt
        )

    def delete_project_milestone(self, milestone_id: int, *, project_id: int) -> None:
        row = self._infra.database.get_project_milestone(milestone_id)
        if not row or int(row.get("project_id") or 0) != int(project_id):
            raise ValueError("Meilenstein nicht gefunden oder falsches Projekt")
        self._infra.database.delete_project_milestone(milestone_id)

    def set_project_milestones_sort_order(self, project_id: int, milestone_ids_in_order: List[int]) -> None:
        ids = [int(x) for x in milestone_ids_in_order]
        if not ids:
            return
        all_rows = self._infra.database.list_project_milestones(project_id)
        valid = {int(r["milestone_id"]) for r in all_rows}
        if set(ids) != valid or len(ids) != len(valid):
            raise ValueError("Meilenstein-Reihenfolge: ID-Menge passt nicht zum Projekt")
        self._infra.database.set_project_milestones_sort_order(project_id, ids)


_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """Liefert den globalen ProjectService."""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service


def set_project_service(service: Optional[ProjectService]) -> None:
    """Setzt den ProjectService (für Tests)."""
    global _project_service
    _project_service = service
