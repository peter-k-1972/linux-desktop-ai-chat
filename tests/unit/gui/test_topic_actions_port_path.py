"""topic_actions: Port-Pfad ohne Service (reine Weiterleitung)."""

from __future__ import annotations

from app.gui.domains.operations.chat.panels.topic_actions import (
    assign_chat_to_topic,
    remove_chat_from_topic,
)


class _FakeOps:
    def __init__(self) -> None:
        self.moves: list[tuple[int, int, int | None]] = []

    def move_chat_to_topic(
        self, project_id: int, chat_id: int, topic_id: int | None
    ) -> None:
        self.moves.append((project_id, chat_id, topic_id))


def test_assign_chat_to_topic_uses_port():
    ops = _FakeOps()
    assert assign_chat_to_topic(1, 2, 3, chat_ops=ops) is True
    assert ops.moves == [(1, 2, 3)]


def test_remove_chat_from_topic_uses_port_ungrouped():
    ops = _FakeOps()
    assert remove_chat_from_topic(10, 20, chat_ops=ops) is True
    assert ops.moves == [(10, 20, None)]
