"""
State-Consistency: Agent bearbeitet -> Profil -> Registry.

Agent bearbeitet -> Profil zeigt neue Werte -> Registry liefert neue Werte.
"""

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_service import AgentService


@pytest.fixture
def temp_db_path():
    import os
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def agent_service(temp_db_path):
    repo = AgentRepository(db_path=temp_db_path)
    return AgentService(repository=repo)


def test_agent_update_registry_consistency(agent_service):
    """
    Nach Update muss die Registry dieselben Werte liefern wie der Service.
    """
    profile = AgentProfile(
        id=None,
        name="Consistency-Agent",
        display_name="Consistency",
        slug="consistency_agent",
        department="research",
        status=AgentStatus.ACTIVE.value,
        system_prompt="Original-Prompt",
        short_description="Original",
    )
    agent_id, _ = agent_service.create(profile)
    assert agent_id is not None

    registry = AgentRegistry(repository=agent_service._repo)
    registry.refresh()

    # Service und Registry müssen übereinstimmen
    from_service = agent_service.get(agent_id)
    from_registry = registry.get(agent_id)
    assert from_service.system_prompt == from_registry.system_prompt
    assert from_service.short_description == from_registry.short_description

    # Update
    from_service.short_description = "Aktualisiert"
    from_service.system_prompt = "Neuer System-Prompt"
    agent_service.update(from_service)

    # Registry muss nach refresh neue Werte liefern
    registry.refresh()
    from_registry_after = registry.get(agent_id)
    assert from_registry_after.short_description == "Aktualisiert"
    assert from_registry_after.system_prompt == "Neuer System-Prompt"


@pytest.mark.state_consistency
@pytest.mark.ui
@pytest.mark.regression
def test_agent_ui_save_registry_consistency(qtbot, temp_db_path):
    """
    Bearbeiten in UI -> Speichern -> Registry.refresh() -> gleiche Werte.
    Verhindert: UI-Save aktualisiert nicht die Registry.
    """
    from unittest.mock import patch
    from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel
    from app.agents.agent_service import AgentService

    repo = AgentRepository(db_path=temp_db_path)
    service = AgentService(repository=repo)
    registry = AgentRegistry(repository=repo)

    profile = AgentProfile(
        id=None,
        name="UI-Registry-Test",
        display_name="UI Registry",
        slug="ui_registry_test",
        department="research",
        status=AgentStatus.ACTIVE.value,
        system_prompt="Original",
        short_description="Original-Desc",
    )
    agent_id, _ = service.create(profile)
    registry.refresh()

    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.get_agent_registry", return_value=registry):
            panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
            qtbot.addWidget(panel)
            panel._refresh_list()
            profile = service.get(agent_id)
            panel._on_agent_selected(profile)

            panel.profile_panel._toggle_edit()
            panel.profile_panel.form.name_edit.setText("Geändert-Name")
            panel.profile_panel.form.short_desc_edit.setText("Geändert-Beschreibung")
            panel._on_save(panel.profile_panel.form.to_profile(profile))
            qtbot.wait(100)

    registry.refresh()
    from_registry = registry.get(agent_id)
    assert from_registry.name == "Geändert-Name"
    assert from_registry.short_description == "Geändert-Beschreibung"
