"""ServiceChatPortAdapter: Kontextmenü- und Topic-Aktionen delegieren korrekt."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.ui_application.adapters.service_chat_port_adapter import ServiceChatPortAdapter


def test_list_projects_for_chat_move_excludes_current():
    mock_ps = MagicMock()
    mock_ps.list_projects.return_value = [
        {"project_id": 1, "name": "Keep"},
        {"project_id": 2, "name": "Other"},
    ]
    with patch(
        "app.services.project_service.get_project_service", return_value=mock_ps
    ):
        a = ServiceChatPortAdapter()
        rows = a.list_projects_for_chat_move(1)
    assert len(rows) == 1
    assert rows[0].project_id == 2
    assert rows[0].name == "Other"


def test_create_topic_delegates():
    mock_ts = MagicMock()
    mock_ts.create_topic.return_value = 42
    with patch(
        "app.services.topic_service.get_topic_service", return_value=mock_ts
    ):
        a = ServiceChatPortAdapter()
        tid = a.create_topic(5, "T", "")
    assert tid == 42
    mock_ts.create_topic.assert_called_once_with(5, "T", "")


def test_delete_chat_delegates():
    mock_cs = MagicMock()
    with patch(
        "app.services.chat_service.get_chat_service", return_value=mock_cs
    ):
        a = ServiceChatPortAdapter()
        a.delete_chat(9)
    mock_cs.delete_chat.assert_called_once_with(9)


def test_set_active_project_selection_delegates():
    mock_mgr = MagicMock()
    with patch(
        "app.core.context.project_context_manager.get_project_context_manager",
        return_value=mock_mgr,
    ):
        a = ServiceChatPortAdapter()
        a.set_active_project_selection(5)
        mock_mgr.set_active_project.assert_called_once_with(5)
        mock_mgr.reset_mock()
        a.set_active_project_selection(None)
        mock_mgr.set_active_project.assert_called_once_with(None)
