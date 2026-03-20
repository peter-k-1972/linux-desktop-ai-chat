"""
AgentService – Agentenliste, Agent starten, Agentstatus.

Fassade über app.agents.AgentService (CRUD) und AgentTaskRunner (Ausführung).
Verantwortlich für:
- Agentenliste
- Agent starten (Task)
- Agentstatus / Aktivität (via DebugStore)

GUI spricht nur mit AgentService, nicht mit AgentRepository oder Ollama direkt.
"""

from typing import Any, Dict, List, Optional

from app.agents.agent_profile import AgentProfile
from app.services.result import ServiceResult


class AgentService:
    """
    Fassade für Agenten-Operationen.
    Delegiert an app.agents.agent_service und agent_task_runner.
    """

    def __init__(self):
        pass

    def list_agents(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet Agenten mit optionaler Filterung."""
        return self.list_agents_for_project(
            project_id=None,
            department=department,
            status=status,
            filter_text=filter_text,
        )

    def list_agents_for_project(
        self,
        project_id: Optional[int],
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet Agenten für ein Projekt (globale + projektspezifische)."""
        from app.agents.agent_service import get_agent_service as _get_crud
        return _get_crud().list_for_project(
            project_id=project_id,
            department=department,
            status=status,
            filter_text=filter_text,
        )

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten."""
        from app.agents.agent_service import get_agent_service as _get_crud
        return _get_crud().get(agent_id)

    def get_agent_by_slug(self, slug: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten nach Slug."""
        from app.agents.agent_service import get_agent_service as _get_crud
        return _get_crud().get_by_slug(slug)

    async def start_agent_task(
        self,
        agent_id: str,
        prompt: str,
        model_override: Optional[str] = None,
    ):
        """
        Startet einen Agent-Task.
        Returns: AgentTaskResult (von agent_task_runner).
        """
        from app.agents.agent_task_runner import get_agent_task_runner
        runner = get_agent_task_runner()
        return await runner.start_agent_task(agent_id, prompt, model_override)

    def get_active_tasks(self) -> List[Any]:
        """Lädt aktive Tasks aus DebugStore."""
        from app.debug.debug_store import get_debug_store
        return get_debug_store().get_active_tasks()

    def get_agent_status(self) -> Dict[str, str]:
        """Lädt Agent-Status aus DebugStore."""
        from app.debug.debug_store import get_debug_store
        return get_debug_store().get_agent_status()

    def get_event_history(self) -> List[Any]:
        """Lädt Event-Historie aus DebugStore."""
        from app.debug.debug_store import get_debug_store
        return get_debug_store().get_event_history()

    # CRUD – delegiert an app.agents.AgentService
    def create_agent(self, profile: AgentProfile) -> ServiceResult[Optional[str]]:
        """Erstellt einen Agenten. Returns: (agent_id, error)."""
        from app.agents.agent_service import get_agent_service as _get_crud
        agent_id, err = _get_crud().create(profile)
        if err:
            return ServiceResult.fail(err)
        return ServiceResult.ok(agent_id)

    def update_agent(self, profile: AgentProfile) -> ServiceResult[bool]:
        """Aktualisiert einen Agenten."""
        from app.agents.agent_service import get_agent_service as _get_crud
        ok, err = _get_crud().update(profile)
        if err:
            return ServiceResult.fail(err)
        return ServiceResult.ok(ok)

    def delete_agent(self, agent_id: str) -> ServiceResult[bool]:
        """Löscht einen Agenten."""
        from app.agents.agent_service import get_agent_service as _get_crud
        ok, err = _get_crud().delete(agent_id)
        if err:
            return ServiceResult.fail(err)
        return ServiceResult.ok(ok)


_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Liefert den globalen AgentService (Fassade)."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
