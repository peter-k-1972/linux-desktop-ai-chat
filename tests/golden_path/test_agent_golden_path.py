"""
Golden-Path 3: Agent anlegen -> speichern -> Profil öffnen -> bearbeiten -> löschen.

Prüft den vollständigen Agent-CRUD-Flow mit Registry-Sync.
"""

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_repository import AgentRepository
from app.agents.agent_service import AgentService


@pytest.mark.golden_path
def test_agent_create_save_load_edit_delete(agent_service, temp_db_path):
    """
    Golden Path: Agent erstellen -> in Liste/Registry -> laden ->
    bearbeiten -> speichern -> Registry liefert neue Werte -> löschen -> weg.
    """
    # 1. Anlegen & Speichern
    profile = AgentProfile(
        id=None,
        name="Golden-Path-Agent",
        display_name="GP Agent",
        slug="golden_path_agent",
        department="research",
        status=AgentStatus.ACTIVE.value,
        system_prompt="Du bist ein Test-Assistent.",
        short_description="Kurzbeschreibung",
    )
    agent_id, err = agent_service.create(profile)
    assert err is None
    assert agent_id is not None

    # 2. In Liste und Registry
    agents = agent_service.list_all()
    assert any(a.id == agent_id for a in agents)

    registry = AgentRegistry(repository=agent_service._repo)
    registry.refresh()
    found = registry.get(agent_id)
    assert found is not None
    assert found.system_prompt == "Du bist ein Test-Assistent."

    # 3. Profil laden (get)
    loaded = agent_service.get(agent_id)
    assert loaded.name == "Golden-Path-Agent"
    assert loaded.short_description == "Kurzbeschreibung"

    # 4. Bearbeiten & Speichern
    loaded.short_description = "Neue Beschreibung nach Bearbeitung"
    loaded.system_prompt = "Neuer System-Prompt."
    ok, err = agent_service.update(loaded)
    assert err is None
    assert ok is True

    # 5. Registry liefert neue Werte (Konsistenz)
    registry.refresh()
    updated = registry.get(agent_id)
    assert updated.short_description == "Neue Beschreibung nach Bearbeitung"
    assert updated.system_prompt == "Neuer System-Prompt."

    # 6. Löschen
    ok, err = agent_service.delete(agent_id)
    assert err is None
    assert ok is True

    # 7. Weg aus Service und Registry
    assert agent_service.get(agent_id) is None
    registry.refresh()
    assert registry.get(agent_id) is None
    assert agent_id not in [a.id for a in agent_service.list_all()]
