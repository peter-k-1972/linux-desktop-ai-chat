"""
Agent Factory – erzeugt Agent-Instanzen aus Profilen.

Verbindet Profile mit der Laufzeit-Architektur (BaseAgent).
"""

from typing import Any, Dict, Optional

from app.agents.agent_base import ProfileAgent
from app.agents.agent_profile import AgentProfile
from app.agents.agent_registry import get_agent_registry


class AgentFactory:
    """Erzeugt Agent-Instanzen aus Profilen."""

    def __init__(self):
        self._registry = get_agent_registry()

    def create_from_profile(self, profile: AgentProfile) -> ProfileAgent:
        """Erstellt einen ProfileAgent aus einem Profil."""
        return ProfileAgent(profile)

    def create_from_id(self, agent_id: str) -> Optional[ProfileAgent]:
        """Erstellt einen Agent aus einer ID."""
        profile = self._registry.get(agent_id)
        if not profile:
            return None
        return self.create_from_profile(profile)

    def create_from_slug(self, slug: str) -> Optional[ProfileAgent]:
        """Erstellt einen Agent aus einem Slug."""
        profile = self._registry.get_by_slug(slug)
        if not profile:
            return None
        return self.create_from_profile(profile)


def get_agent_factory() -> AgentFactory:
    """Liefert die globale Agent-Factory."""
    return AgentFactory()
