"""ChatContextInspector: Topic-Liste und Verschieben über Port (ohne Service im Hauptpfad)."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.inspector.chat_context_inspector import ChatContextInspector


def _qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


class _FakeOps:
    def __init__(self) -> None:
        self.list_calls: list[int] = []
        self.moves: list[tuple[int, int, int | None]] = []

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        self.list_calls.append(project_id)
        return [{"id": 10, "name": "Alpha"}]

    def move_chat_to_topic(
        self, project_id: int, chat_id: int, topic_id: int | None
    ) -> None:
        self.moves.append((project_id, chat_id, topic_id))


def test_inspector_populates_topics_from_port(qapp):
    ops = _FakeOps()
    w = ChatContextInspector(
        project_id=7,
        chat_id=3,
        chat_ops=ops,
    )
    assert ops.list_calls == [7]
    assert w._topic_combo is not None
    assert w._topic_combo.count() >= 2


def test_inspector_without_port_still_builds(qapp):
    w = ChatContextInspector(project_id=None, chat_id=None, chat_ops=None)
    assert w._topic_combo is None
