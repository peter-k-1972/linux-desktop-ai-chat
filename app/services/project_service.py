"""
ProjectService – Projekte, Zuordnungen, Statistiken.

Zentrale API für Projekt-Operationen. Nutzt DatabaseManager.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from app.chat.context_policies import ChatContextPolicy

from app.services.infrastructure import get_infrastructure


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
    ) -> int:
        """Erstellt ein Projekt. Gibt project_id zurück."""
        return self._infra.database.create_project(
            name, description, status, default_context_policy
        )

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
    ) -> None:
        """Aktualisiert Projektfelder."""
        self._infra.database.update_project(
            project_id, name, description, status, default_context_policy
        )

    def delete_project(self, project_id: int) -> None:
        """Löscht ein Projekt und alle Zuordnungen."""
        self._infra.database.delete_project(project_id)

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

    def count_chats_of_project(self, project_id: int) -> int:
        """Anzahl Chats eines Projekts."""
        return self._infra.database.count_chats_of_project(project_id)

    def count_files_of_project(self, project_id: int) -> int:
        """Anzahl Dateien eines Projekts."""
        return self._infra.database.count_files_of_project(project_id)

    def count_prompts_of_project(self, project_id: int) -> int:
        """Anzahl Prompts eines Projekts."""
        return self._infra.database.count_prompts_of_project(project_id)

    # --- Aktiver Projektkontext (delegiert an ActiveProjectContext) ---

    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Liefert das aktuell aktive Projekt oder None."""
        try:
            from app.core.context.active_project import get_active_project_context
            return get_active_project_context().active_project
        except Exception:
            return None

    def get_active_project_id(self) -> Optional[int]:
        """Liefert die ID des aktiven Projekts oder None."""
        try:
            from app.core.context.active_project import get_active_project_context
            return get_active_project_context().active_project_id
        except Exception:
            return None

    def set_active_project(self, project_id: Optional[int] = None, project: Optional[Dict[str, Any]] = None) -> None:
        """Setzt das aktive Projekt. Lädt Projektdaten falls nur project_id übergeben."""
        try:
            from app.core.context.active_project import get_active_project_context
            if project_id is not None and project is None:
                project = self.get_project(project_id)
            get_active_project_context().set_active(project_id=project_id, project=project)
        except Exception:
            pass

    def clear_active_project(self) -> None:
        """Entfernt den aktiven Projektkontext."""
        try:
            from app.core.context.active_project import get_active_project_context
            get_active_project_context().set_none()
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
