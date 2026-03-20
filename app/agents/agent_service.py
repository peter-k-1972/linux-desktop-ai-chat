"""
Agent Service – CRUD, Validierung, UI-Anbindung.

Fassade für alle Agenten-Operationen mit Fehlerbehandlung.
"""

import logging
from typing import List, Optional, Tuple

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.departments import department_from_str, all_departments, Department
from app.core.models.roles import ModelRole, all_roles

logger = logging.getLogger(__name__)


class AgentValidationError(Exception):
    """Validierungsfehler bei Agenten."""

    pass


class AgentService:
    """CRUD und Validierung für Agenten."""

    def __init__(self, repository: Optional[AgentRepository] = None):
        self._repo = repository or AgentRepository()

    def create(self, profile: AgentProfile) -> Tuple[Optional[str], Optional[str]]:
        """
        Erstellt einen neuen Agenten.
        Returns: (agent_id, error_message)
        """
        err = self._validate(profile, for_create=True)
        if err:
            return None, err
        try:
            agent_id = self._repo.create(profile)
            return agent_id, None
        except Exception as e:
            logger.exception("Agent create failed")
            return None, str(e)

    def update(self, profile: AgentProfile) -> Tuple[bool, Optional[str]]:
        """
        Aktualisiert einen Agenten.
        Returns: (success, error_message)
        """
        if not profile.id:
            return False, "Keine Agent-ID"
        err = self._validate(profile, for_create=False)
        if err:
            return False, err
        try:
            ok = self._repo.update(profile)
            return ok, None
        except Exception as e:
            logger.exception("Agent update failed")
            return False, str(e)

    def delete(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """Löscht einen Agenten."""
        if not agent_id:
            return False, "Keine Agent-ID"
        try:
            ok = self._repo.delete(agent_id)
            return ok, None if ok else "Agent nicht gefunden"
        except Exception as e:
            logger.exception("Agent delete failed")
            return False, str(e)

    def get(self, agent_id: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten."""
        return self._repo.get(agent_id)

    def get_by_slug(self, slug: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten nach Slug."""
        return self._repo.get_by_slug(slug)

    def list_all(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet Agenten mit optionaler Filterung."""
        return self._repo.list_all(department=department, status=status, filter_text=filter_text)

    def list_for_project(
        self,
        project_id: Optional[int],
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet Agenten für ein Projekt (globale + projektspezifische)."""
        return self._repo.list_for_project(
            project_id=project_id,
            department=department,
            status=status,
            filter_text=filter_text,
        )

    def duplicate(self, agent_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Dupliziert einen Agenten (neuer Name, neue ID).
        Returns: (new_agent_id, error_message)
        """
        orig = self._repo.get(agent_id)
        if not orig:
            return None, "Agent nicht gefunden"
        copy = AgentProfile(
            id=None,
            project_id=orig.project_id,
            name=f"{orig.name} (Kopie)",
            display_name=f"{orig.display_name or orig.name} (Kopie)",
            slug="",
            short_description=orig.short_description,
            long_description=orig.long_description,
            department=orig.department,
            role=orig.role,
            status=AgentStatus.INACTIVE.value,
            avatar_path=orig.avatar_path,
            avatar_id=orig.avatar_id,
            assigned_model=orig.assigned_model,
            assigned_model_role=orig.assigned_model_role,
            system_prompt=orig.system_prompt,
            capabilities=list(orig.capabilities),
            tools=list(orig.tools),
            knowledge_spaces=list(orig.knowledge_spaces),
            tags=list(orig.tags),
            memory_config=orig.memory_config,
            limits_config=orig.limits_config,
            personality_style=orig.personality_style,
            response_style=orig.response_style,
            escalation_policy=orig.escalation_policy,
            fallback_model=orig.fallback_model,
            ui_color=orig.ui_color,
            theme_hint=orig.theme_hint,
            visibility_in_chat=orig.visibility_in_chat,
            priority=orig.priority,
            cloud_allowed=orig.cloud_allowed,
            workflow_bindings=list(orig.workflow_bindings),
            external_command_hooks=list(orig.external_command_hooks),
            media_pipeline_capabilities=list(orig.media_pipeline_capabilities),
            output_types=list(orig.output_types),
        )
        return self.create(copy)

    def set_status(self, agent_id: str, status: str) -> Tuple[bool, Optional[str]]:
        """Setzt den Status eines Agenten."""
        if status not in (AgentStatus.ACTIVE.value, AgentStatus.INACTIVE.value, AgentStatus.ARCHIVED.value):
            return False, f"Ungültiger Status: {status}"
        profile = self._repo.get(agent_id)
        if not profile:
            return False, "Agent nicht gefunden"
        profile.status = status
        return self.update(profile)

    def activate(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """Aktiviert einen Agenten."""
        return self.set_status(agent_id, AgentStatus.ACTIVE.value)

    def deactivate(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """Deaktiviert einen Agenten."""
        return self.set_status(agent_id, AgentStatus.INACTIVE.value)

    def _validate(self, profile: AgentProfile, for_create: bool) -> Optional[str]:
        """Validiert ein Profil. Gibt Fehlermeldung zurück oder None."""
        if not (profile.name or "").strip():
            return "Name ist erforderlich"
        name = profile.name.strip()
        if for_create:
            existing = self._repo.get_by_name(name)
            if existing:
                return f"Ein Agent mit dem Namen '{name}' existiert bereits"
        else:
            existing = self._repo.get_by_name(name)
            if existing and existing.id != profile.id:
                return f"Ein anderer Agent mit dem Namen '{name}' existiert bereits"

        if profile.department:
            dept = department_from_str(profile.department)
            if dept is None and profile.department not in [d.value for d in all_departments()]:
                return f"Unbekannte Abteilung: {profile.department}"

        if profile.assigned_model_role:
            try:
                ModelRole(profile.assigned_model_role)
            except ValueError:
                return f"Unbekannte Modellrolle: {profile.assigned_model_role}"

        valid_statuses = {AgentStatus.ACTIVE.value, AgentStatus.INACTIVE.value, AgentStatus.ARCHIVED.value}
        if profile.status and profile.status not in valid_statuses:
            return f"Ungültiger Status: {profile.status}"

        return None


# Singleton für App-weite Nutzung
_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Liefert den globalen AgentService."""
    global _service
    if _service is None:
        _service = AgentService()
    return _service
