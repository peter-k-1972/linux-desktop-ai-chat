"""Navigation-Panel: mit nav_data kein Pfad über get_chat_service für Listen-Refresh."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.chat.panels.chat_navigation_panel import ChatNavigationPanel


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


class _FakeNavData:
    def __init__(self) -> None:
        self.list_calls: list[tuple[Any, ...]] = []

    def list_chats_for_navigation(
        self,
        project_id: int | None,
        filter_text: str,
        *,
        topic_id: int | None = None,
        pinned_only: bool | None = None,
        archived_only: bool | None = None,
        recent_days: int | None = None,
    ) -> list[dict[str, Any]]:
        self.list_calls.append(
            (project_id, filter_text, topic_id, pinned_only, archived_only, recent_days)
        )
        return [
            {
                "id": 1,
                "title": "T1",
                "archived": False,
                "pinned": False,
                "last_activity": "2025-01-01",
            }
        ]

    def create_chat_for_navigation(
        self, project_id: int | None, *, topic_id: int | None = None
    ) -> int:
        return 99

    def chat_item_menu_context(
        self, chat_id: int, panel_project_id: int | None
    ) -> tuple[str, int | None, list[dict[str, Any]]]:
        return ("x", panel_project_id, [])

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        return []


def test_refresh_uses_nav_data_not_services(qapp):
    fake = _FakeNavData()
    panel = ChatNavigationPanel(nav_data=fake)
    panel.set_project(1, "P")
    panel.refresh()
    assert any(c[0] == 1 for c in fake.list_calls), fake.list_calls
