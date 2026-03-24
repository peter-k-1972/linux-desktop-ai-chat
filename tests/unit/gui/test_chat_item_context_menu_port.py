"""Kontextmenü: mit chat_ops keine Service-Imports im Aktionspfad (Smoke)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.chat.panels.chat_item_context_menu import (
    build_chat_item_context_menu,
)


def _qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


class _RecordingOps:
    def save_chat_title(self, chat_id: int, title: str) -> None:
        self.last = ("title", chat_id, title)

    def move_chat_to_topic(
        self, project_id: int, chat_id: int, topic_id: int | None
    ) -> None:
        self.last = ("move", project_id, chat_id, topic_id)

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        self.last = ("pin", project_id, chat_id, pinned)

    def set_chat_archived(
        self, project_id: int, chat_id: int, archived: bool
    ) -> None:
        self.last = ("arch", project_id, chat_id, archived)

    def duplicate_chat(
        self, chat_id: int, project_id: int, topic_id: int | None = None
    ) -> int | None:
        self.last = ("dup", chat_id, project_id, topic_id)
        return 100

    def delete_chat(self, chat_id: int) -> None:
        self.last = ("del", chat_id)

    def list_projects_for_chat_move(self, exclude_project_id: int | None):
        from app.ui_contracts.workspaces.chat import ProjectListRow

        return (ProjectListRow(project_id=99, name="X"),)

    def move_chat_to_project(self, chat_id: int, target_project_id: int) -> None:
        self.last = ("mproj", chat_id, target_project_id)

    def set_active_project_selection(self, project_id: object | None) -> None:
        self.last = ("active", project_id)

    def create_topic(self, project_id: int, name: str, description: str = "") -> int:
        return 0

    def update_topic_name(self, topic_id: int, name: str) -> None:
        pass

    def delete_topic_by_id(self, topic_id: int) -> None:
        pass


def test_build_chat_item_menu_with_ops_has_actions(qapp):
    ops = _RecordingOps()
    menu = build_chat_item_context_menu(
        project_id=1,
        chat_id=2,
        chat_title="Hi",
        current_topic_id=3,
        is_pinned=False,
        is_archived=False,
        topics=[{"id": 4, "name": "T"}],
        parent_widget=None,
        on_action=lambda: None,
        chat_ops=ops,
    )
    assert menu.actions()


def test_build_context_bar_menu_with_ops(qapp):
    from app.gui.domains.operations.chat.panels.chat_item_context_menu import (
        build_context_bar_context_menu,
    )

    ops = _RecordingOps()
    menu = build_context_bar_context_menu(
        chat_id=2,
        project_id=1,
        chat_title="Hi",
        current_topic_id=None,
        is_pinned=False,
        is_archived=False,
        topics=[],
        parent_widget=None,
        on_action=lambda: None,
        on_project_switch_requested=lambda: None,
        on_new_chat_requested=lambda: None,
        chat_ops=ops,
    )
    assert menu.actions()
