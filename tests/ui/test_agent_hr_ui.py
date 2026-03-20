"""
UI Tests: Agent HR Panel.

Testet Agent erstellen, bearbeiten, löschen, Profil anzeigen.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QPushButton, QComboBox
from PySide6.QtCore import Qt

from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel
from app.gui.domains.control_center.agents_ui.agent_profile_panel import AgentProfilePanel
from app.gui.domains.control_center.agents_ui.agent_list_panel import AgentListPanel
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_service import AgentService
from app.agents.agent_repository import AgentRepository


@pytest.fixture
def agent_service_with_data(temp_db_path):
    """AgentService mit Test-Agent."""
    repo = AgentRepository(db_path=temp_db_path)
    service = AgentService(repository=repo)
    profile = AgentProfile(
        id=None,
        name="UI-Test-Agent",
        display_name="UI Test",
        slug="ui_test_agent",
        department="research",
        status=AgentStatus.ACTIVE.value,
    )
    agent_id, _ = service.create(profile)
    return service, agent_id


def test_agent_manager_panel_opens(qtbot, temp_db_path):
    """Agent-Manager-Panel öffnet ohne Fehler."""
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        repo = AgentRepository(db_path=temp_db_path)
        service = AgentService(repository=repo)
        panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
        qtbot.addWidget(panel)
        panel.show()
        assert panel.isVisible()
        assert panel.new_btn is not None
        assert panel.delete_btn is not None


def test_agent_manager_new_button_clickable(qtbot, temp_db_path):
    """Neu-Button ist klickbar."""
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        repo = AgentRepository(db_path=temp_db_path)
        service = AgentService(repository=repo)
        panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
        qtbot.addWidget(panel)
        qtbot.mouseClick(panel.new_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(50)


@pytest.mark.ui
@pytest.mark.regression
def test_agent_new_button_creates_agent_in_list(qtbot, temp_db_path):
    """
    Neu klicken -> Agent in Liste, auswählbar.
    Verhindert: Neu-Button ohne Effekt.
    """
    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        repo = AgentRepository(db_path=temp_db_path)
        service = AgentService(repository=repo)
        panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
        qtbot.addWidget(panel)
        panel._refresh_list()
        count_before = panel.list_panel.list_widget.count()

        qtbot.mouseClick(panel.new_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(150)

        count_after = panel.list_panel.list_widget.count()
        assert count_after >= count_before + 1, "Neu-Button muss neuen Agent in Liste erzeugen"

        agents_in_service = service.list_all()
        assert len(agents_in_service) >= 1
        new_agent = next((a for a in agents_in_service if a.name == "Neuer Agent"), None)
        assert new_agent is not None


def test_agent_list_panel_opens(qtbot):
    """AgentListPanel zeigt Agentenliste."""
    panel = AgentListPanel(theme="dark")
    qtbot.addWidget(panel)
    panel.set_agents([
        AgentProfile(id="1", name="Agent A", slug="a", department="research"),
        AgentProfile(id="2", name="Agent B", slug="b", department="development"),
    ])
    panel.show()
    assert panel.isVisible()


def test_agent_profile_panel_opens(qtbot):
    """AgentProfilePanel zeigt Profil-Formular."""
    panel = AgentProfilePanel(theme="dark")
    panel.set_model_options(["llama3", "mistral"])
    qtbot.addWidget(panel)
    panel.show()
    assert panel.isVisible()


def test_agent_profile_panel_loads_profile(qtbot):
    """AgentProfilePanel lädt Agent-Profil – sichtbare Labels zeigen Profil-Daten."""
    panel = AgentProfilePanel(theme="dark")
    qtbot.addWidget(panel)
    profile = AgentProfile(
        id="p1",
        name="Loaded-Agent",
        display_name="Loaded",
        slug="loaded",
        short_description="Kurzbeschreibung",
        department="research",
    )
    panel.load_profile(profile)
    # Verhalten: Profil-Daten müssen in sichtbaren Labels erscheinen
    assert "Loaded" in panel.name_label.text() or "Loaded-Agent" in panel.name_label.text()
    assert "Kurzbeschreibung" in panel.desc_label.text()


def test_agent_manager_delete_button(qtbot, temp_db_path, agent_service_with_data):
    """Löschen-Button löscht ausgewählten Agenten – Agent darf danach nicht mehr in Liste sein."""
    from PySide6.QtWidgets import QMessageBox

    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        with patch(
            "app.gui.domains.control_center.agents_ui.agent_manager_panel.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            service, agent_id = agent_service_with_data
            panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
            qtbot.addWidget(panel)
            panel._refresh_list()
            profile = service.get(agent_id)
            panel._on_agent_selected(profile)
            # Liste muss den Agenten ausgewählt haben – get_selected() liest von list_widget
            list_w = panel.list_panel.list_widget
            for i in range(list_w.count()):
                item = list_w.item(i)
                p = item.data(Qt.ItemDataRole.UserRole) if item else None
                if p and p.id == agent_id:
                    list_w.setCurrentItem(item)
                    break
            qtbot.mouseClick(panel.delete_btn, Qt.MouseButton.LeftButton)
            qtbot.wait(100)
        agents = service.list_all()
        agent_ids = [a.id for a in agents]
        assert agent_id not in agent_ids, "Gelöschter Agent darf nicht mehr in Liste sein"
        # UI-Ebene: list_widget darf den Agenten nicht mehr enthalten
        list_w = panel.list_panel.list_widget
        list_agent_ids = []
        for i in range(list_w.count()):
            item = list_w.item(i)
            p = item.data(Qt.ItemDataRole.UserRole) if item else None
            if p and p.id:
                list_agent_ids.append(p.id)
        assert agent_id not in list_agent_ids, "Gelöschter Agent darf nicht mehr in list_widget sein"
