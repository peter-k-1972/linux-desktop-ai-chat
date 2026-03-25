"""ChatDetailsPanel: Contract-State anzeigen, Mutationen über Fake-Port."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.chat.panels.chat_details_panel import ChatDetailsPanel
from app.ui_contracts import ChatDetailsPanelState, ChatTopicOptionEntry


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


class _FakeOps:
    def __init__(self) -> None:
        self.moves: list[tuple[int, int, int | None]] = []

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        return []

    def move_chat_to_topic(self, project_id: int, chat_id: int, topic_id: int | None) -> None:
        self.moves.append((project_id, chat_id, topic_id))

    def save_chat_title(self, chat_id: int, title: str) -> None:
        pass

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        pass

    def set_chat_archived(self, project_id: int, chat_id: int, archived: bool) -> None:
        pass


def test_apply_details_state_sets_title(qapp):
    panel = ChatDetailsPanel(details_ops=_FakeOps())
    st = ChatDetailsPanelState(
        chat_id=1,
        title="Hello",
        project_id=2,
        project_name="P",
        selected_topic_id=None,
        topic_display_name=None,
        topic_options=(ChatTopicOptionEntry(None, "Ungruppiert"),),
        model_label="m1",
        last_assistant_agent=None,
        created_at_label="01.01.2025 00:00",
        updated_at_label="02.01.2025 00:00",
        is_pinned=False,
        is_archived=False,
    )
    panel.apply_details_state(st)
    assert "Hello" in panel._title_label.text()
    assert "m1" in panel._model_label.text()


def test_smoke_chat_workspace_has_details_ops(qapp):
    from app.gui.domains.operations.chat.chat_workspace import ChatWorkspace

    w = ChatWorkspace()
    assert w._details_panel._details_ops is not None
