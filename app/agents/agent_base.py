"""
Agent Base – abstrakte Basis für alle Agenten.

Erweitert um ProfileAgent für die Agenten-Farm und Chat-Integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.agent_profile import AgentProfile


class BaseAgent(ABC):
    """
    Abstrakte Basis für Agenten.
    """

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Eindeutige Agent-ID."""
        pass

    @abstractmethod
    async def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Führt den Agenten aus.

        Args:
            prompt: User-Eingabe
            context: Zusätzlicher Kontext (z.B. RAG-Chunks, Historie)

        Returns:
            Agent-Ausgabe
        """
        pass


class ProfileAgent(BaseAgent):
    """
    Agent mit vollständigem Profil.
    Nutzt Profil für Modell, System-Prompt, Fähigkeiten.
    """

    def __init__(self, profile: AgentProfile):
        self._profile = profile

    @property
    def profile(self) -> AgentProfile:
        return self._profile

    @property
    def agent_id(self) -> str:
        return self._profile.id or ""

    def get_model(self) -> Optional[str]:
        """Liefert das zugewiesene Modell."""
        return self._profile.assigned_model

    def get_model_role(self):
        """Liefert die zugewiesene Modellrolle (ModelRole-Enum)."""
        return self._profile.get_model_role_enum()

    def get_system_prompt(self) -> str:
        """Liefert den System-Prompt des Agenten."""
        return self._profile.system_prompt or ""

    def get_context(self) -> Dict[str, Any]:
        """Liefert Kontext für den Agenten (Profil, Fähigkeiten, etc.)."""
        return {
            "profile": self._profile.to_dict(),
            "capabilities": self._profile.capabilities,
            "tools": self._profile.tools,
            "knowledge_spaces": self._profile.knowledge_spaces,
        }

    def can_handle(self, task: str) -> bool:
        """
        Prüft, ob der Agent eine Aufgabe übernehmen kann.
        Einfache Heuristik: prüft capabilities und department.
        """
        if not self._profile.is_active:
            return False
        task_lower = (task or "").lower()
        for cap in self._profile.capabilities:
            if cap.lower() in task_lower or task_lower in cap.lower():
                return True
        return False

    async def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Führt den Agenten aus.
        ProfileAgent delegiert an eine Chat-Funktion – diese muss von außen injiziert werden.
        Für direkte Ausführung: create_research_agent oder ChatWidget.run_chat mit Agent.
        """
        raise NotImplementedError(
            "ProfileAgent.run() erfordert injizierte Chat-Funktion. "
            "Nutze ChatWidget mit aktivem Agent oder create_research_agent für Research."
        )
