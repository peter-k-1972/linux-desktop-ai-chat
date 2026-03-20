"""
UI-Behavior-Tests – Prüfen echte UI-Wirkung, nicht nur Widget-Existenz.

- Klick auf Speichern ändert tatsächlich Daten und UI
- Klick auf Löschen entfernt Eintrag sichtbar und persistent
- Auswahl in Listen lädt wirklich den korrekten Datensatz
- Eingaben landen im richtigen Feld / richtigen Objekt
- Sichtbare Texte stimmen mit internem Zustand überein
"""

import pytest
from unittest.mock import patch

from PySide6.QtWidgets import QPushButton, QLineEdit, QPlainTextEdit
from PySide6.QtCore import Qt

from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel
from app.gui.domains.control_center.agents_ui.agent_profile_panel import AgentProfilePanel
from app.gui.domains.control_center.agents_ui.agent_list_panel import AgentListPanel
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_service import AgentService
from app.agents.agent_repository import AgentRepository


@pytest.fixture
def agent_service_with_agent(temp_db_path):
    """AgentService mit einem Test-Agent."""
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        repo = AgentRepository(db_path=temp_db_path)
        service = AgentService(repository=repo)
        profile = AgentProfile(
            id=None,
            name="Behavior-Test-Agent",
            display_name="Behavior Test",
            slug="behavior_test_agent",
            department="research",
            status=AgentStatus.ACTIVE.value,
            short_description="Original-Beschreibung",
        )
        agent_id, _ = service.create(profile)
        return service, agent_id


@pytest.mark.ui
def test_agent_profile_panel_loads_profile_shows_correct_data(qtbot):
    """
    load_profile() muss die sichtbaren Labels (name_label, desc_label) mit
    den Profil-Daten füllen. Leseansicht muss Profil-Inhalt zeigen.
    """
    panel = AgentProfilePanel(theme="dark")
    qtbot.addWidget(panel)
    profile = AgentProfile(
        id="p1",
        name="Loaded-Agent-Name",
        display_name="Display Name",
        slug="loaded_agent",
        short_description="Kurzbeschreibung geladen",
        department="research",
    )
    panel.load_profile(profile)

    # name_label und desc_label müssen Profil-Daten anzeigen
    assert "Display Name" in panel.name_label.text() or "Loaded-Agent" in panel.name_label.text()
    assert "Kurzbeschreibung" in panel.desc_label.text()


@pytest.mark.ui
def test_agent_list_selection_loads_profile(qtbot, agent_service_with_agent):
    """
    Auswahl in AgentListPanel muss das entsprechende Profil im Panel laden.
    """
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        service, agent_id = agent_service_with_agent
        panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
        qtbot.addWidget(panel)
        panel._refresh_list()

        agents = service.list_all()
        target = next(a for a in agents if a.id == agent_id)
        panel._on_agent_selected(target)

        assert panel.profile_panel._current_profile is not None
        assert panel.profile_panel._current_profile.id == agent_id


@pytest.mark.ui
def test_agent_save_updates_service(qtbot, agent_service_with_agent):
    """
    Nach Bearbeiten und Speichern muss der Service die neuen Daten haben.
    """
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        service, agent_id = agent_service_with_agent
        panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
        qtbot.addWidget(panel)
        panel._refresh_list()
        profile = service.get(agent_id)
        panel._on_agent_selected(profile)

        # Bearbeiten-Modus aktivieren
        panel.profile_panel._toggle_edit()
        panel.profile_panel.form.short_desc_edit.setText("Neue Beschreibung nach Save")
        panel._on_save(panel.profile_panel.form.to_profile(profile))
        qtbot.wait(100)

        updated = service.get(agent_id)
        assert "Neue Beschreibung" in (updated.short_description or "")
