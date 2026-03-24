"""
GUI-lokales Protocol für ChatDetailsPanel-Mutationen (ohne direkte Service-Imports im Panel).

Implementierung: typischerweise :class:`ServiceChatPortAdapter`.
"""

from __future__ import annotations

from typing import Any, Protocol


class ChatDetailsDataSource(Protocol):
    """Topic-Liste und Chat-Metadaten-Aktionen wie bisher über ChatService."""

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        ...

    def move_chat_to_topic(self, project_id: int, chat_id: int, topic_id: int | None) -> None:
        ...

    def save_chat_title(self, chat_id: int, title: str) -> None:
        ...

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        ...

    def set_chat_archived(self, project_id: int, chat_id: int, archived: bool) -> None:
        ...
