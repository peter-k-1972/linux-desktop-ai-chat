"""
ChatOperationsPort — Qt-frei, service-neutral (nur Typen + Mapping/Dicts).

Implementierungen leben in ``adapters/`` und delegieren an ``app.services``.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable

from app.ui_contracts.workspaces.chat import ChatListEntry, ChatWorkspaceState, ProjectListRow


@runtime_checkable
class ChatOperationsPort(Protocol):
    """Zentrale Chat-Operationen für ChatPresenter und ChatWorkspace (ohne ORM-Objekte)."""

    # --- Liste / Auswahl ---
    def list_chat_entries(self, filter_text: str) -> list[ChatListEntry]:
        """Session-Liste für Explorer (bereits gemappte Contract-Einträge)."""
        ...

    def load_conversation_rows(self, chat_id: int) -> list[tuple[Any, ...]]:
        """Rohzeilen wie ``ChatService.load_chat`` für ``ChatConversationPanel.load_messages``."""
        ...

    # --- Nachrichten / Chat-Lebenszyklus ---
    def get_chat_info(self, chat_id: int) -> dict[str, Any] | None:
        """Metadaten-Dict (Titel, Topic, Pin, …) oder None."""
        ...

    def create_chat_global(self, title: str) -> int:
        ...

    def create_chat_in_project(self, project_id: int, title: str) -> int:
        ...

    def save_user_message(self, chat_id: int, text: str) -> None:
        """Persistiert Nutzernachricht (Rolle user)."""
        ...

    def save_assistant_message(
        self,
        chat_id: int,
        content: str,
        *,
        model: str,
        completion_status: str | None,
    ) -> None:
        ...

    def save_chat_title(self, chat_id: int, title: str) -> None:
        ...

    def maybe_autotitle_from_first_message(self, chat_id: int, user_text: str) -> bool:
        """
        Wenn Titel noch leer/„Neuer Chat“, aus Nutzertext ableiten.
        Gibt True zurück, wenn ein Titel gesetzt wurde.
        """
        ...

    def build_api_messages(self, chat_id: int) -> list[dict[str, str]]:
        """Konversationshistorie als API-Liste (role/content)."""
        ...

    # --- Projekt / Kontext ---
    def project_id_for_chat(self, chat_id: int) -> int | None:
        ...

    def get_project_record(self, project_id: int) -> dict[str, Any] | None:
        ...

    def get_active_project_id(self) -> int | None:
        ...

    def get_active_project_record(self) -> dict[str, Any] | None:
        ...

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        """Topic-Liste für Kontextmenüs (rohe Dicts, GUI bleibt unverändert)."""
        ...

    def move_chat_to_topic(self, project_id: int, chat_id: int, topic_id: int | None) -> None:
        """Ordnet den Chat einem Topic zu; ``topic_id`` None = ungruppiert."""
        ...

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        ...

    def set_chat_archived(self, project_id: int, chat_id: int, archived: bool) -> None:
        ...

    # --- Kontextmenü Chat-Liste / Kontextleiste (Delegation, keine neue Fachlogik) ---
    def duplicate_chat(
        self, chat_id: int, project_id: int, topic_id: int | None = None
    ) -> int | None:
        """Kopie des Chats im gleichen Projekt (optional gleiches Topic)."""
        ...

    def delete_chat(self, chat_id: int) -> None:
        ...

    def list_projects_for_chat_move(self, exclude_project_id: int | None) -> tuple[ProjectListRow, ...]:
        """Alle Projekte außer ``exclude_project_id`` für „Chat verschieben zu…“."""
        ...

    def move_chat_to_project(self, chat_id: int, target_project_id: int) -> None:
        """Wie ``ProjectService.move_chat_to_project`` (ohne aktives Projekt zu wechseln)."""
        ...

    def set_active_project_id(self, project_id: int) -> None:
        """Aktives App-Projekt setzen (z. B. nach Chat-Verschiebung)."""
        ...

    def set_active_project_selection(self, project_id: object | None) -> None:
        """Wie ``project_context_manager.set_active_project`` (Switcher, ``None`` = Kontext leeren)."""
        ...

    # --- Topic-Aktionen (Navigation / Header-Menü) ---
    def create_topic(self, project_id: int, name: str, description: str = "") -> int:
        ...

    def update_topic_name(self, topic_id: int, name: str) -> None:
        ...

    def delete_topic_by_id(self, topic_id: int) -> None:
        ...

    # --- ChatNavigationPanel (Rohdicts, keine neue Fachlogik) ---
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
        """Wie ``list_chats_for_project`` — nur Delegation im Adapter."""
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
        ...

    # --- Modelle ---
    async def load_unified_model_catalog(
        self,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """
        (catalog_entries, default_selection_id) wie bisherige Combo-Logik.
        """
        ...

    def get_stream_settings(self) -> tuple[float, int, bool]:
        """temperature, max_tokens, stream_enabled."""
        ...

    # --- Streaming / Completion ---
    def iter_chat_chunks(
        self,
        *,
        model: str,
        chat_id: int,
        api_messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """Async-Stream roher Provider-Chunks (Presenter + Assembler verarbeiten)."""
        ...

    def merge_invocation_payload(
        self, prior: dict[str, Any] | None, chunk: dict[str, Any]
    ) -> dict[str, Any] | None:
        ...

    def invocation_error_kind(self, chunk: dict[str, Any]) -> str | None:
        ...

    def completion_status_for_outcome(
        self,
        full_content: str,
        *,
        provider_finished_normally: bool,
        had_error: bool,
        had_exception: bool,
    ) -> str | None:
        """DB-String für completion_status (oder None)."""
        ...

    def build_chat_invocation_view(
        self,
        merged_invocation: dict[str, Any] | None,
        *,
        last_error_text: str | None,
        last_error_kind: str | None,
        completion_status_db: str | None,
        model_name: str,
    ) -> dict[str, Any]:
        ...

    def get_last_assistant_agent_for_chat(self, chat_id: int) -> str | None:
        ...

    def cancel_generation(self) -> None:
        """
        Stream-Abbruch: ``ChatService`` bietet keinen Cancel-Hook — Methode bleibt No-Op.

        UI-Zustand: ``StopGenerationCommand`` setzt Contract-State über
        ``stop_generation_state`` (stream_phase idle); kein Provider-Abbruch.
        """
        ...

    # --- Presenter-Zustand (optional, schrittweise) ---
    def load_workspace_bootstrap(self) -> ChatWorkspaceState:
        """Kalter Zustand für Contract-Pfad (kann Minimalzustand sein)."""
        ...

    def select_chat_state(self, state: ChatWorkspaceState, chat_id: int | None) -> ChatWorkspaceState:
        ...

    def create_chat_state(self, state: ChatWorkspaceState, title: str) -> ChatWorkspaceState:
        ...

    def rename_chat_state(self, state: ChatWorkspaceState, chat_id: int, title: str) -> ChatWorkspaceState:
        ...

    def apply_filter_state(self, state: ChatWorkspaceState, filter_text: str) -> ChatWorkspaceState:
        ...

    def stop_generation_state(self, state: ChatWorkspaceState) -> ChatWorkspaceState:
        ...
