"""
Regression: Agent gelöscht, aber noch in Liste sichtbar.

Bug: Löschen-Button klicken → Agent wurde aus DB entfernt, aber die UI-Liste
zeigte den Agenten weiterhin an, bis manuell neu geladen wurde.

Erwartung: Nach delete() darf der gelöschte Agent nicht mehr in list_all() sein.
"""

import pytest
from unittest.mock import patch

from PySide6.QtCore import Qt

from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_service import AgentService
from app.agents.agent_repository import AgentRepository


@pytest.mark.regression
def test_agent_delete_removes_from_service_list(agent_service):
    """
    Nach Löschen darf der Agent nicht mehr in service.list_all() erscheinen.
    """
    profile = AgentProfile(
        id=None,
        name="To-Delete-Agent",
        display_name="Delete Me",
        slug="to_delete_agent",
        department="research",
        status=AgentStatus.ACTIVE.value,
    )
    agent_id, err = agent_service.create(profile)
    assert err is None
    assert agent_id is not None

    ids_before = [a.id for a in agent_service.list_all()]
    assert agent_id in ids_before

    ok, err = agent_service.delete(agent_id)
    assert err is None
    assert ok is True

    ids_after = [a.id for a in agent_service.list_all()]
    assert agent_id not in ids_after


@pytest.mark.regression
@pytest.mark.ui
def test_agent_delete_removes_from_ui_list(qtbot, temp_db_path):
    """
    Nach Löschen darf der Agent nicht mehr in der Agent-Liste sein.
    Ruft _on_delete direkt auf (mit gepatchtem QMessageBox), um modalen Dialog zu vermeiden.
    """
    from PySide6.QtWidgets import QMessageBox

    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        with patch(
            "app.gui.domains.control_center.agents_ui.agent_manager_panel.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            repo = AgentRepository(db_path=temp_db_path)
            service = AgentService(repository=repo)
            profile = AgentProfile(
                id=None,
                name="UI-Delete-Test",
                display_name="UI Delete",
                slug="ui_delete_test",
                department="research",
                status=AgentStatus.ACTIVE.value,
            )
            agent_id, _ = service.create(profile)

            panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
            qtbot.addWidget(panel)
            panel._refresh_list()
            panel._on_agent_selected(service.get(agent_id))

            # Liste muss den Agenten ausgewählt haben – get_selected() liest von list_widget
            list_w = panel.list_panel.list_widget
            for i in range(list_w.count()):
                item = list_w.item(i)
                p = item.data(Qt.ItemDataRole.UserRole) if item else None
                if p and p.id == agent_id:
                    list_w.setCurrentItem(item)
                    break

            # _on_delete direkt aufrufen (QMessageBox ist gepatcht)
            panel._on_delete()
            qtbot.wait(50)

    # Agent darf nicht mehr in der Liste sein (Service)
    agents = service.list_all()
    agent_ids = [a.id for a in agents]
    assert agent_id not in agent_ids

    # list_widget darf den gelöschten Agenten nicht mehr enthalten (UI-Ebene)
    list_w = panel.list_panel.list_widget
    list_agent_ids = []
    for i in range(list_w.count()):
        item = list_w.item(i)
        p = item.data(Qt.ItemDataRole.UserRole) if item else None
        if p and p.id:
            list_agent_ids.append(p.id)
    assert agent_id not in list_agent_ids, "Gelöschter Agent darf nicht mehr in list_widget sein"


@pytest.mark.regression
@pytest.mark.ui
@pytest.mark.cross_layer
def test_deleted_selected_agent_falls_back_cleanly(qtbot, temp_db_path):
    """
    Gelöschter Agent war ausgewählt -> Nach Refresh enthält Combo den Agent nicht mehr.
    Verhindert: Stale Agent-Referenz in Chat/Header nach Löschen.
    """
    from PySide6.QtWidgets import QMessageBox
    from app.gui.domains.operations.chat.panels.chat_header_widget import ChatHeaderWidget

    with patch("app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        with patch(
            "app.gui.domains.control_center.agents_ui.agent_manager_panel.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            repo = AgentRepository(db_path=temp_db_path)
            service = AgentService(repository=repo)
            profile = AgentProfile(
                id=None,
                name="Stale-Test-Agent",
                display_name="Stale Test",
                slug="stale_test_agent",
                department="research",
                status=AgentStatus.ACTIVE.value,
            )
            agent_id, _ = service.create(profile)

            header = ChatHeaderWidget(theme="dark")
            header.agent_combo.clear()
            header.agent_combo.addItem("Standard (kein Agent)", None)
            header.agent_combo.addItem(profile.display_name, agent_id)
            header.agent_combo.setCurrentIndex(1)
            assert header.agent_combo.currentData() == agent_id

            panel = AgentManagerPanel(agent_service=service, theme="dark", model_ids=[])
            qtbot.addWidget(panel)
            panel._refresh_list()
            panel._on_agent_selected(service.get(agent_id))

            list_w = panel.list_panel.list_widget
            for i in range(list_w.count()):
                item = list_w.item(i)
                p = item.data(Qt.ItemDataRole.UserRole) if item else None
                if p and p.id == agent_id:
                    list_w.setCurrentItem(item)
                    break

            panel._on_delete()
            qtbot.wait(100)

            header.agent_combo.clear()
            header.agent_combo.addItem("Standard (kein Agent)", None)
            for a in service.list_all():
                header.agent_combo.addItem(a.effective_display_name, a.id)

            combo_ids = [
                header.agent_combo.itemData(i)
                for i in range(header.agent_combo.count())
            ]
            assert agent_id not in combo_ids, (
                "Gelöschter Agent darf nach Refresh nicht mehr in Agent-Combo sein"
            )
