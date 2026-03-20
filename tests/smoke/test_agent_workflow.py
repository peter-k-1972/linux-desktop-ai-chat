"""
Smoke Tests: Agent Workflow.

Testet Agent auswählen, Task starten, Ergebnis erhalten.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_factory import AgentFactory
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_repository import AgentRepository
from app.agents.agent_base import ProfileAgent


@pytest.fixture
def agent_workflow_setup(temp_db_path):
    """Setup für Agent-Workflow-Tests."""
    repo = AgentRepository(db_path=temp_db_path)
    profile = AgentProfile(
        id=None,
        name="Workflow-Test-Agent",
        display_name="Workflow Test",
        slug="workflow_test",
        department="research",
        status=AgentStatus.ACTIVE.value,
        capabilities=["research", "analysis"],
        system_prompt="Du bist ein Test-Assistent.",
    )
    agent_id = repo.create(profile)
    profile.id = agent_id
    registry = AgentRegistry(repository=repo)
    registry.refresh()
    factory = AgentFactory()
    factory._registry = registry
    return factory, registry, profile


def test_agent_select_from_registry(agent_workflow_setup):
    """Agent kann aus Registry ausgewählt werden."""
    factory, registry, profile = agent_workflow_setup
    found = registry.get(profile.id)
    assert found is not None
    assert found.name == "Workflow-Test-Agent"


def test_agent_factory_creates_from_profile(agent_workflow_setup):
    """AgentFactory erstellt Agent aus Profil."""
    factory, registry, profile = agent_workflow_setup
    agent = factory.create_from_profile(profile)
    assert isinstance(agent, ProfileAgent)
    assert agent.agent_id == profile.id


def test_agent_factory_creates_from_id(agent_workflow_setup):
    """AgentFactory erstellt Agent aus ID."""
    factory, registry, profile = agent_workflow_setup
    agent = factory.create_from_id(profile.id)
    assert agent is not None
    assert agent.profile.name == "Workflow-Test-Agent"


def test_agent_can_handle_task(agent_workflow_setup):
    """Agent kann Task anhand Capabilities prüfen."""
    factory, registry, profile = agent_workflow_setup
    agent = factory.create_from_profile(profile)
    assert agent.can_handle("Research zu Thema X") is True
    assert agent.can_handle("Kochen") is False


def test_agent_get_context(agent_workflow_setup):
    """Agent liefert Kontext für LLM."""
    factory, registry, profile = agent_workflow_setup
    agent = factory.create_from_profile(profile)
    ctx = agent.get_context()
    assert "profile" in ctx
    assert "capabilities" in ctx
    assert "research" in ctx["capabilities"]


def test_agent_get_system_prompt(agent_workflow_setup):
    """Agent liefert System-Prompt."""
    factory, registry, profile = agent_workflow_setup
    agent = factory.create_from_profile(profile)
    prompt = agent.get_system_prompt()
    assert "Test-Assistent" in prompt
