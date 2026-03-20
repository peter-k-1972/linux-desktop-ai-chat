"""
Agent Registry – zentrale Registratur aller Agenten.

Liefert Agenten nach id, name, department, role.
Verwaltet aktive/inaktive Agenten für Chat-Integration.
"""

from typing import Dict, List, Optional

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.departments import Department


class AgentRegistry:
    """
    Registry für alle Agenten.
    Lädt bei Bedarf aus dem Repository und cached für schnellen Zugriff.
    """

    def __init__(self, repository: Optional[AgentRepository] = None):
        self._repo = repository or AgentRepository()
        self._cache: Dict[str, AgentProfile] = {}
        self._slug_index: Dict[str, str] = {}  # slug -> id
        self._name_index: Dict[str, str] = {}  # name -> id

    def refresh(self) -> None:
        """Lädt alle Agenten neu und baut Indizes auf."""
        self._cache.clear()
        self._slug_index.clear()
        self._name_index.clear()
        for p in self._repo.list_all():
            self._cache[p.id] = p
            if p.slug:
                self._slug_index[p.slug] = p.id
            if p.name:
                self._name_index[p.name] = p.id

    def get(self, agent_id: str) -> Optional[AgentProfile]:
        """Liefert einen Agenten nach ID."""
        if agent_id in self._cache:
            return self._cache[agent_id]
        p = self._repo.get(agent_id)
        if p:
            self._cache[p.id] = p
            if p.slug:
                self._slug_index[p.slug] = p.id
            if p.name:
                self._name_index[p.name] = p.id
        return p

    def get_by_slug(self, slug: str) -> Optional[AgentProfile]:
        """Liefert einen Agenten nach Slug."""
        if slug in self._slug_index:
            return self.get(self._slug_index[slug])
        p = self._repo.get_by_slug(slug)
        if p:
            self._cache[p.id] = p
            self._slug_index[p.slug] = p.id
            if p.name:
                self._name_index[p.name] = p.id
        return p

    def get_by_name(self, name: str) -> Optional[AgentProfile]:
        """Liefert einen Agenten nach Name."""
        if name in self._name_index:
            return self.get(self._name_index[name])
        p = self._repo.get_by_name(name)
        if p:
            self._cache[p.id] = p
            if p.slug:
                self._slug_index[p.slug] = p.id
            self._name_index[p.name] = p.id
        return p

    def list_by_department(self, department: Department) -> List[AgentProfile]:
        """Liefert alle Agenten einer Abteilung."""
        return self._repo.list_all(department=department.value)

    def list_by_status(self, status: str) -> List[AgentProfile]:
        """Liefert alle Agenten mit einem bestimmten Status."""
        return self._repo.list_all(status=status)

    def list_active(self) -> List[AgentProfile]:
        """Liefert alle aktiven Agenten (sichtbar im Chat)."""
        return [
            p
            for p in self._repo.list_all()
            if p.status == AgentStatus.ACTIVE.value and p.visibility_in_chat
        ]

    def list_all(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet Agenten mit optionaler Filterung."""
        return self._repo.list_all(department=department, status=status, filter_text=filter_text)

    def register_profile(self, profile: AgentProfile) -> None:
        """Fügt ein Profil zum Cache hinzu (nach Create/Update)."""
        if profile.id:
            self._cache[profile.id] = profile
            if profile.slug:
                self._slug_index[profile.slug] = profile.id
            if profile.name:
                self._name_index[profile.name] = profile.id

    def unregister(self, agent_id: str) -> None:
        """Entfernt ein Profil aus dem Cache (nach Delete)."""
        p = self._cache.pop(agent_id, None)
        if p:
            if p.slug and self._slug_index.get(p.slug) == agent_id:
                del self._slug_index[p.slug]
            if p.name and self._name_index.get(p.name) == agent_id:
                del self._name_index[p.name]


# Singleton
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Liefert die globale Agent-Registry."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
