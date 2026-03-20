"""
Contract Tests: AgentProfile-Struktur.

Sichert den Vertrag zwischen AgentProfile und allen Konsumenten
(AgentService, AgentRegistry, ChatWidget, UI-Panels).
"""

from datetime import datetime, timezone

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus


# Pflichtfelder, die alle Konsumenten erwarten
REQUIRED_AGENT_PROFILE_FIELDS = [
    "id",
    "name",
    "display_name",
    "slug",
    "short_description",
    "long_description",
    "department",
    "role",
    "status",
    "system_prompt",
    "capabilities",
    "tools",
    "knowledge_spaces",
    "tags",
    "visibility_in_chat",
    "priority",
]


@pytest.mark.contract
def test_agent_profile_to_dict_contains_required_fields(test_agent):
    """AgentProfile.to_dict() liefert alle Pflichtfelder für Konsumenten."""
    d = test_agent.to_dict()
    for field in REQUIRED_AGENT_PROFILE_FIELDS:
        assert field in d, f"Pflichtfeld '{field}' fehlt in to_dict()"


@pytest.mark.contract
def test_agent_profile_from_dict_roundtrip(test_agent):
    """AgentProfile: to_dict → from_dict erhält alle relevanten Daten."""
    d = test_agent.to_dict()
    restored = AgentProfile.from_dict(d)
    assert restored.id == test_agent.id
    assert restored.name == test_agent.name
    assert restored.display_name == test_agent.display_name
    assert restored.slug == test_agent.slug
    assert restored.department == test_agent.department
    assert restored.status == test_agent.status
    assert restored.system_prompt == test_agent.system_prompt
    assert restored.capabilities == test_agent.capabilities
    assert restored.tools == test_agent.tools
    assert restored.visibility_in_chat == test_agent.visibility_in_chat
    assert restored.priority == test_agent.priority


@pytest.mark.contract
def test_agent_profile_from_dict_handles_minimal_input():
    """AgentProfile.from_dict() akzeptiert minimales Dict (Default-Werte)."""
    minimal = {"name": "Minimal"}
    p = AgentProfile.from_dict(minimal)
    assert p.name == "Minimal"
    assert p.department == "general"
    assert p.status == "active"
    assert p.capabilities == []
    assert p.tools == []
    assert p.visibility_in_chat is True
    assert p.priority == 0


@pytest.mark.contract
def test_agent_profile_status_values():
    """AgentStatus-Enum-Werte sind stabil für Persistenz."""
    assert AgentStatus.ACTIVE.value == "active"
    assert AgentStatus.INACTIVE.value == "inactive"
    assert AgentStatus.ARCHIVED.value == "archived"


@pytest.mark.contract
def test_agent_profile_list_fields_serialize_as_lists(test_agent):
    """capabilities, tools, tags etc. werden als Listen serialisiert."""
    d = test_agent.to_dict()
    assert isinstance(d["capabilities"], list)
    assert isinstance(d["tools"], list)
    assert isinstance(d["tags"], list)
    assert isinstance(d["knowledge_spaces"], list)
