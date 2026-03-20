"""
Unit Tests: Agent System.

Testet AgentProfile, AgentRegistry, AgentService, AgentFactory isoliert.
"""

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_service import AgentService
from app.agents.agent_factory import AgentFactory
from app.agents.agent_base import ProfileAgent
from app.agents.departments import Department


# --- AgentProfile ---

def test_agent_profile_to_dict(test_agent):
    """AgentProfile.to_dict() serialisiert korrekt."""
    d = test_agent.to_dict()
    assert d["name"] == "Test-Research-Agent"
    assert d["department"] == "research"
    assert d["status"] == "active"
    assert "rag" in d["tools"]
    assert "research" in d["capabilities"]


def test_agent_profile_from_dict(test_agent):
    """AgentProfile.from_dict() deserialisiert korrekt."""
    d = test_agent.to_dict()
    restored = AgentProfile.from_dict(d)
    assert restored.name == test_agent.name
    assert restored.department == test_agent.department
    assert restored.tools == test_agent.tools


def test_agent_profile_slugify():
    """Slugify erzeugt gültige Slugs."""
    p = AgentProfile(name="Mein Agent mit Sonderzeichen!")
    assert AgentProfile._slugify("Test Agent") == "test_agent"
    assert AgentProfile._slugify("") == "agent"


def test_agent_profile_is_active(test_agent, test_agent_inactive):
    """is_active Property funktioniert."""
    assert test_agent.is_active is True
    assert test_agent_inactive.is_active is False


def test_agent_profile_effective_display_name(test_agent):
    """effective_display_name nutzt display_name oder name."""
    assert test_agent.effective_display_name == "Research Agent (Test)"
    p = AgentProfile(name="OnlyName")
    assert p.effective_display_name == "OnlyName"


def test_agent_profile_get_department_enum(test_agent):
    """get_department_enum() liefert Department-Enum."""
    dept = test_agent.get_department_enum()
    assert dept == Department.RESEARCH


# --- AgentRegistry ---

def test_agent_registry_register_and_get(agent_repository, test_agent):
    """Registry speichert und liefert Profile."""
    agent_repository.create(test_agent)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    found = registry.get(test_agent.id)
    assert found is not None
    assert found.name == test_agent.name


def test_agent_registry_get_by_slug(agent_repository, test_agent):
    """Registry findet Agent per Slug."""
    agent_repository.create(test_agent)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    found = registry.get_by_slug("test_research_agent")
    assert found is not None
    assert found.slug == "test_research_agent"


def test_agent_registry_list_active(agent_repository, test_agent, test_agent_inactive):
    """list_active() filtert nur aktive, sichtbare Agenten."""
    agent_repository.create(test_agent)
    agent_repository.create(test_agent_inactive)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    active = registry.list_active()
    names = [a.name for a in active]
    assert "Test-Research-Agent" in names
    assert "Test-Inactive-Agent" not in names


def test_agent_registry_unregister(agent_repository, test_agent):
    """unregister() entfernt aus Cache."""
    agent_repository.create(test_agent)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    registry.unregister(test_agent.id)
    assert test_agent.id not in registry._cache  # Aus Cache entfernt
    assert registry.get(test_agent.id) is not None  # DB hat noch den Eintrag


# --- AgentService ---

def test_agent_service_create(agent_repository, test_agent):
    """AgentService.create() erstellt Agenten."""
    service = AgentService(repository=agent_repository)
    test_agent.id = None
    test_agent.name = "Unique-Test-Agent-123"
    agent_id, err = service.create(test_agent)
    assert err is None
    assert agent_id is not None
    loaded = service.get(agent_id)
    assert loaded.name == "Unique-Test-Agent-123"


def test_agent_service_create_validation_empty_name(agent_repository):
    """Create lehnt leeren Namen ab."""
    service = AgentService(repository=agent_repository)
    profile = AgentProfile(name="", department="research")
    agent_id, err = service.create(profile)
    assert agent_id is None
    assert "Name" in err or "erforderlich" in err.lower()


def test_agent_service_update(agent_repository, test_agent):
    """AgentService.update() aktualisiert Agenten."""
    agent_repository.create(test_agent)
    service = AgentService(repository=agent_repository)
    test_agent.short_description = "Neue Beschreibung"
    ok, err = service.update(test_agent)
    assert err is None
    assert ok is True
    loaded = service.get(test_agent.id)
    assert loaded.short_description == "Neue Beschreibung"


def test_agent_service_delete(agent_repository, test_agent):
    """AgentService.delete() löscht Agenten."""
    agent_repository.create(test_agent)
    service = AgentService(repository=agent_repository)
    ok, err = service.delete(test_agent.id)
    assert err is None
    assert ok is True
    assert service.get(test_agent.id) is None


def test_agent_service_duplicate(agent_repository, test_agent):
    """AgentService.duplicate() erstellt Kopie."""
    agent_repository.create(test_agent)
    service = AgentService(repository=agent_repository)
    new_id, err = service.duplicate(test_agent.id)
    assert err is None
    assert new_id != test_agent.id
    copied = service.get(new_id)
    assert "Kopie" in copied.name


def test_agent_service_set_status(agent_repository, test_agent):
    """set_status, activate, deactivate funktionieren."""
    agent_repository.create(test_agent)
    service = AgentService(repository=agent_repository)
    ok, err = service.deactivate(test_agent.id)
    assert err is None and ok is True
    loaded = service.get(test_agent.id)
    assert loaded.status == AgentStatus.INACTIVE.value
    ok, err = service.activate(test_agent.id)
    assert err is None and ok is True


# --- AgentFactory ---

def test_agent_factory_create_from_profile(test_agent):
    """AgentFactory erstellt ProfileAgent aus Profil."""
    factory = AgentFactory()
    agent = factory.create_from_profile(test_agent)
    assert isinstance(agent, ProfileAgent)
    assert agent.agent_id == test_agent.id
    assert agent.get_system_prompt() == test_agent.system_prompt


def test_agent_factory_create_from_id(agent_repository, test_agent):
    """AgentFactory erstellt Agent aus ID."""
    agent_repository.create(test_agent)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    factory = AgentFactory()
    factory._registry = registry
    agent = factory.create_from_id(test_agent.id)
    assert agent is not None
    assert agent.agent_id == test_agent.id


def test_agent_factory_create_from_slug(agent_repository, test_agent):
    """AgentFactory erstellt Agent aus Slug."""
    agent_repository.create(test_agent)
    registry = AgentRegistry(repository=agent_repository)
    registry.refresh()
    factory = AgentFactory()
    factory._registry = registry
    agent = factory.create_from_slug("test_research_agent")
    assert agent is not None
    assert agent.profile.slug == "test_research_agent"


def test_profile_agent_can_handle(test_agent):
    """ProfileAgent.can_handle() prüft Capabilities."""
    agent = ProfileAgent(test_agent)
    # Capability "research" muss in Task vorkommen
    assert agent.can_handle("Research zu Thema X") is True
    assert agent.can_handle("Analyse mit research") is True
    assert agent.can_handle("Kochen") is False
