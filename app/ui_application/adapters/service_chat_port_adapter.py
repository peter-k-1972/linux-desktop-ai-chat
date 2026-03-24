"""
Adapter: bestehende Services → :class:`ChatOperationsPort`.

Ein zentraler Ort für Service-Zugriffe des Chat-Workspaces (Presenter-Pfad).
Keine neue Fachlogik — nur Delegation und triviale Mapping-Schritte.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import replace
from typing import Any

from app.ui_application.mappers.chat_details_mapper import build_chat_details_panel_state, empty_chat_details_panel_state
from app.ui_application.mappers.chat_mapper import chat_list_entry_from_mapping, chat_message_from_row
from app.ui_contracts.common.enums import ChatConnectionStatus, ChatStreamPhase, ChatWorkspaceLoadState
from app.ui_contracts.workspaces.chat import (
    ChatListEntry,
    ChatMessageEntry,
    ChatWorkspaceState,
    ProjectContextEntry,
    ProjectListRow,
)


def _model_label_from_messages(msgs: tuple[ChatMessageEntry, ...]) -> str | None:
    for m in reversed(msgs):
        if m.role == "assistant":
            ml = (m.model_label or "").strip()
            return ml or None
    return None


def _messages_from_rows(rows: list[tuple[Any, ...]]) -> tuple[ChatMessageEntry, ...]:
    out: list[ChatMessageEntry] = []
    for i, row in enumerate(rows):
        d: dict[str, Any] = {
            "role": row[0],
            "content": row[1] if len(row) > 1 else "",
        }
        if len(row) > 3 and row[3] is not None:
            d["model"] = row[3]
        out.append(chat_message_from_row(d, message_index=i))
    return tuple(out)


class ServiceChatPortAdapter:
    """Konkreter Port über Chat-/Projekt-/Topic-/Model-Services."""

    def list_chat_entries(self, filter_text: str) -> list[ChatListEntry]:
        from app.services.chat_service import get_chat_service

        pid = self.get_active_project_id()
        raw = get_chat_service().list_chats_for_project(pid, filter_text=filter_text)
        return [chat_list_entry_from_mapping(c) for c in raw]

    def load_conversation_rows(self, chat_id: int) -> list[tuple[Any, ...]]:
        from app.services.chat_service import get_chat_service

        return list(get_chat_service().load_chat(chat_id))

    def get_chat_info(self, chat_id: int) -> dict[str, Any] | None:
        from app.services.chat_service import get_chat_service

        return get_chat_service().get_chat_info(chat_id)

    def create_chat_global(self, title: str) -> int:
        from app.services.chat_service import get_chat_service

        return get_chat_service().create_chat(title)

    def create_chat_in_project(self, project_id: int, title: str) -> int:
        from app.services.chat_service import get_chat_service

        return get_chat_service().create_chat_in_project(project_id, title)

    def save_user_message(self, chat_id: int, text: str) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().save_message(chat_id, "user", text)

    def save_assistant_message(
        self,
        chat_id: int,
        content: str,
        *,
        model: str,
        completion_status: str | None,
    ) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().save_message(
            chat_id,
            "assistant",
            content,
            model=model,
            completion_status=completion_status,
        )

    def save_chat_title(self, chat_id: int, title: str) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().save_chat_title(chat_id, title)

    def maybe_autotitle_from_first_message(self, chat_id: int, user_text: str) -> bool:
        from app.services.chat_service import get_chat_service

        chat_svc = get_chat_service()
        info = chat_svc.get_chat_info(chat_id)
        if not info:
            return False
        t = (info.get("title") or "").strip()
        if t and t != "Neuer Chat":
            return False
        title = (user_text[:50] + "…") if len(user_text) > 50 else user_text
        chat_svc.save_chat_title(chat_id, title)
        return True

    def build_api_messages(self, chat_id: int) -> list[dict[str, str]]:
        rows = self.load_conversation_rows(chat_id)
        return [{"role": str(r[0]), "content": str(r[1]) if len(r) > 1 else ""} for r in rows]

    def project_id_for_chat(self, chat_id: int) -> int | None:
        from app.services.project_service import get_project_service

        return get_project_service().get_project_of_chat(chat_id)

    def get_project_record(self, project_id: int) -> dict[str, Any] | None:
        from app.services.project_service import get_project_service

        return get_project_service().get_project(project_id)

    def get_active_project_id(self) -> int | None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            return get_project_context_manager().get_active_project_id()
        except Exception:
            return None

    def get_active_project_record(self) -> dict[str, Any] | None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            p = get_project_context_manager().get_active_project()
            return p if isinstance(p, dict) else None
        except Exception:
            return None

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        from app.services.topic_service import get_topic_service

        return list(get_topic_service().list_topics_for_project(project_id))

    def move_chat_to_topic(self, project_id: int, chat_id: int, topic_id: int | None) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().move_chat_to_topic(project_id, chat_id, topic_id)

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().set_chat_pinned(project_id, chat_id, pinned)

    def set_chat_archived(self, project_id: int, chat_id: int, archived: bool) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().set_chat_archived(project_id, chat_id, archived)

    def duplicate_chat(
        self, chat_id: int, project_id: int, topic_id: int | None = None
    ) -> int | None:
        from app.services.chat_service import get_chat_service

        return get_chat_service().duplicate_chat(chat_id, project_id, topic_id)

    def delete_chat(self, chat_id: int) -> None:
        from app.services.chat_service import get_chat_service

        get_chat_service().delete_chat(chat_id)

    def list_projects_for_chat_move(self, exclude_project_id: int | None) -> tuple[ProjectListRow, ...]:
        from app.services.project_service import get_project_service

        rows: list[ProjectListRow] = []
        for p in get_project_service().list_projects():
            pid = p.get("project_id")
            if pid is None or pid == exclude_project_id:
                continue
            rows.append(
                ProjectListRow(project_id=int(pid), name=str(p.get("name", "Projekt")))
            )
        return tuple(rows)

    def move_chat_to_project(self, chat_id: int, target_project_id: int) -> None:
        from app.services.project_service import get_project_service

        get_project_service().move_chat_to_project(chat_id, target_project_id)

    def set_active_project_selection(self, project_id: object | None) -> None:
        from app.core.context.project_context_manager import get_project_context_manager

        get_project_context_manager().set_active_project(project_id)

    def set_active_project_id(self, project_id: int) -> None:
        self.set_active_project_selection(project_id)

    def create_topic(self, project_id: int, name: str, description: str = "") -> int:
        from app.services.topic_service import get_topic_service

        return get_topic_service().create_topic(project_id, name, description)

    def update_topic_name(self, topic_id: int, name: str) -> None:
        from app.services.topic_service import get_topic_service

        get_topic_service().update_topic(topic_id, name=name)

    def delete_topic_by_id(self, topic_id: int) -> None:
        from app.services.topic_service import get_topic_service

        get_topic_service().delete_topic(topic_id)

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
        from app.services.chat_service import get_chat_service

        return get_chat_service().list_chats_for_project(
            project_id,
            filter_text,
            topic_id=topic_id,
            pinned_only=pinned_only,
            archived_only=archived_only,
            recent_days=recent_days,
        )

    def create_chat_for_navigation(
        self,
        project_id: int | None,
        *,
        topic_id: int | None = None,
    ) -> int:
        from app.services.chat_service import get_chat_service

        svc = get_chat_service()
        if project_id is not None:
            return svc.create_chat_in_project(project_id, "Neuer Chat", topic_id=topic_id)
        return svc.create_chat("Neuer Chat")

    def chat_item_menu_context(
        self,
        chat_id: int,
        panel_project_id: int | None,
    ) -> tuple[str, int | None, list[dict[str, Any]]]:
        info = self.get_chat_info(chat_id)
        chat_title = info.get("title", "Neuer Chat") if info else "Neuer Chat"
        project_id = panel_project_id
        if project_id is None:
            project_id = self.project_id_for_chat(chat_id)
        topics: list[dict[str, Any]] = []
        if project_id is not None:
            topics = self.list_topic_rows_for_project(project_id)
        return chat_title, project_id, topics

    async def load_unified_model_catalog(
        self,
    ) -> tuple[list[dict[str, Any]], str | None]:
        from app.services.infrastructure import get_infrastructure
        from app.services.model_service import get_model_service
        from app.services.unified_model_catalog_service import get_unified_model_catalog_service

        settings = get_infrastructure().settings
        catalog = await get_unified_model_catalog_service().build_catalog_for_chat(settings)
        selectable = [e["selection_id"] for e in catalog if e.get("chat_selectable")]
        default = None
        if selectable:
            default = get_model_service().get_default_chat_model(selectable)
        return catalog, default

    def get_stream_settings(self) -> tuple[float, int, bool]:
        from app.services.infrastructure import get_infrastructure

        settings = get_infrastructure().settings
        temp = float(getattr(settings, "temperature", 0.7))
        max_tok = int(getattr(settings, "max_tokens", 4096))
        stream = bool(getattr(settings, "chat_streaming_enabled", True))
        return temp, max_tok, stream

    async def iter_chat_chunks(
        self,
        *,
        model: str,
        chat_id: int,
        api_messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        from app.services.chat_service import get_chat_service

        async for chunk in get_chat_service().chat(
            model=model,
            messages=api_messages,
            chat_id=chat_id,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        ):
            yield chunk

    def merge_invocation_payload(
        self, prior: dict[str, Any] | None, chunk: dict[str, Any]
    ) -> dict[str, Any] | None:
        from app.services.model_invocation_display import merge_model_invocation_payload

        return merge_model_invocation_payload(prior, chunk)

    def invocation_error_kind(self, chunk: dict[str, Any]) -> str | None:
        from app.services.model_invocation_display import error_kind_from_chunk

        return error_kind_from_chunk(chunk)

    def completion_status_for_outcome(
        self,
        full_content: str,
        *,
        provider_finished_normally: bool,
        had_error: bool,
        had_exception: bool,
    ) -> str | None:
        from app.chat.completion_heuristics import assess_completion_heuristic
        from app.chat.completion_status import completion_status_to_db

        status = assess_completion_heuristic(
            full_content,
            provider_finished_normally=provider_finished_normally,
            had_error=had_error,
            had_exception=had_exception,
        )
        return completion_status_to_db(status)

    def build_chat_invocation_view(
        self,
        merged_invocation: dict[str, Any] | None,
        *,
        last_error_text: str | None,
        last_error_kind: str | None,
        completion_status_db: str | None,
        model_name: str,
    ) -> dict[str, Any]:
        from app.services.model_invocation_display import build_chat_invocation_view

        return build_chat_invocation_view(
            merged_invocation,
            last_error_text=last_error_text,
            last_error_kind=last_error_kind,
            completion_status_db=completion_status_db,
            model_name=model_name,
        )

    def get_last_assistant_agent_for_chat(self, chat_id: int) -> str | None:
        from app.services.chat_service import get_chat_service

        return get_chat_service().get_last_assistant_agent_for_chat(chat_id)

    def cancel_generation(self) -> None:
        """Kein API-Hook in ChatService/Ollama-Client für laufenden Stream-Abbruch."""
        return

    def load_workspace_bootstrap(self) -> ChatWorkspaceState:
        chats = self.list_chat_entries("")
        pid = self.get_active_project_id()
        prec = self.get_active_project_record()
        name = prec.get("name") if prec else None
        return ChatWorkspaceState(
            load_state=ChatWorkspaceLoadState.IDLE,
            connection=ChatConnectionStatus.UNKNOWN,
            selected_chat_id=None,
            filter_text="",
            chats=tuple(chats),
            messages=(),
            models=(),
            default_model_id=None,
            project=ProjectContextEntry(project_id=pid, name=name),
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
            error=None,
            details_panel=empty_chat_details_panel_state(),
        )

    def select_chat_state(self, state: ChatWorkspaceState, chat_id: int | None) -> ChatWorkspaceState:
        if chat_id is None:
            return replace(
                state,
                selected_chat_id=None,
                messages=(),
                load_state=ChatWorkspaceLoadState.IDLE,
                details_panel=empty_chat_details_panel_state(),
            )
        rows = self.load_conversation_rows(chat_id)
        msgs = _messages_from_rows(rows)
        model_label = _model_label_from_messages(msgs)
        details = build_chat_details_panel_state(self, chat_id, model_label=model_label)
        if details is None:
            details = empty_chat_details_panel_state()
        return replace(
            state,
            selected_chat_id=chat_id,
            messages=msgs,
            load_state=ChatWorkspaceLoadState.IDLE,
            details_panel=details,
        )

    def create_chat_state(self, state: ChatWorkspaceState, title: str) -> ChatWorkspaceState:
        pid = self.get_active_project_id()
        if pid is not None:
            cid = self.create_chat_in_project(pid, title)
        else:
            cid = self.create_chat_global(title)
        return self.select_chat_state(state, cid)

    def rename_chat_state(self, state: ChatWorkspaceState, chat_id: int, title: str) -> ChatWorkspaceState:
        self.save_chat_title(chat_id, title)
        chats = self.list_chat_entries(state.filter_text)
        return replace(state, chats=tuple(chats))

    def apply_filter_state(self, state: ChatWorkspaceState, filter_text: str) -> ChatWorkspaceState:
        chats = self.list_chat_entries(filter_text)
        return replace(state, filter_text=filter_text, chats=tuple(chats))

    def stop_generation_state(self, state: ChatWorkspaceState) -> ChatWorkspaceState:
        self.cancel_generation()
        return replace(
            state,
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
            load_state=ChatWorkspaceLoadState.IDLE,
        )
