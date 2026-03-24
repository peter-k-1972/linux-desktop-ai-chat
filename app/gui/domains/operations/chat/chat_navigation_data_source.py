"""
GUI-lokales Protocol für ChatNavigationPanel-Daten (ohne direkte Service-Imports im Panel).

Implementierung: typischerweise :class:`ServiceChatPortAdapter`.
"""

from __future__ import annotations

from typing import Any, Protocol


class ChatNavigationDataSource(Protocol):
    """Minimale Schnittstelle für Listen, Neuanlage und Kontextmenü-Metadaten."""

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
        """Wie ``ChatService.list_chats_for_project`` (Rohdicts für UI-Gruppierung)."""
        ...

    def create_chat_for_navigation(
        self,
        project_id: int | None,
        *,
        topic_id: int | None = None,
    ) -> int:
        ...

    def chat_item_menu_context(
        self,
        chat_id: int,
        panel_project_id: int | None,
    ) -> tuple[str, int | None, list[dict[str, Any]]]:
        """(chat_title, effective_project_id, topics_rows) für ``build_chat_item_context_menu``."""
        ...

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        ...
