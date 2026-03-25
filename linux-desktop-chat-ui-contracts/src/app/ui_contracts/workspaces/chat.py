"""
Chat-Workspace — Commands, Zustand, Streaming-Patches (Qt-frei).

Alle Strukturen sind für JSON-ähnliche Serialisierung geeignet (primitive + Listen/Dicts).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Literal, Union

from app.ui_contracts.common.enums import (
    ChatConnectionStatus,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
)


@dataclass(frozen=True, slots=True)
class ChatErrorInfo:
    """Fehlerzustand für die Anzeige (kein Stacktrace-Zwang)."""

    code: str
    message: str
    recoverable: bool = True
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ChatListEntry:
    """Eine Zeile in der Chat-Session-Liste."""

    chat_id: int
    title: str
    project_id: int | None = None
    updated_at_iso: str | None = None
    is_archived: bool = False


@dataclass(frozen=True, slots=True)
class ChatMessageEntry:
    """Eine Nachricht in der Konversation (Anzeige-Modell)."""

    message_index: int
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    thinking_text: str | None = None
    model_label: str | None = None
    created_at_iso: str | None = None


@dataclass(frozen=True, slots=True)
class ModelOptionEntry:
    """Auswahl Eintrag im Modell-Dropdown."""

    model_id: str
    label: str
    provider_hint: str | None = None
    is_default: bool = False


@dataclass(frozen=True, slots=True)
class ProjectContextEntry:
    """Aktives Projekt (vereinfacht)."""

    project_id: int | None
    name: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectListRow:
    """Eintrag für Kontextmenü „Chat zu anderem Projekt verschieben“ (id + Anzeigename)."""

    project_id: int
    name: str


@dataclass(frozen=True, slots=True)
class ChatTopicOptionEntry:
    """Eine Zeile im Topic-Dropdown des Detail-Panels (None = ungruppiert)."""

    topic_id: int | None
    label: str


@dataclass(frozen=True, slots=True)
class ChatDetailsPanelState:
    """
    Anzeige + Topic-Optionen für das rechte Metadaten-Panel.

    Zeitstempel sind bereits für die UI formatiert (kein Parsing im Widget).
    """

    chat_id: int | None
    title: str
    project_id: int | None
    project_name: str | None
    selected_topic_id: int | None
    topic_display_name: str | None
    topic_options: tuple[ChatTopicOptionEntry, ...]
    model_label: str | None
    last_assistant_agent: str | None
    created_at_label: str
    updated_at_label: str
    is_pinned: bool
    is_archived: bool


def empty_chat_details_panel_state() -> ChatDetailsPanelState:
    """Leerzustand wenn kein Chat gewählt ist."""
    return ChatDetailsPanelState(
        chat_id=None,
        title="—",
        project_id=None,
        project_name=None,
        selected_topic_id=None,
        topic_display_name=None,
        topic_options=(ChatTopicOptionEntry(None, "Ungruppiert"),),
        model_label=None,
        last_assistant_agent=None,
        created_at_label="—",
        updated_at_label="—",
        is_pinned=False,
        is_archived=False,
    )


@dataclass(frozen=True, slots=True)
class ChatWorkspaceState:
    """Vollständiger Zustand für den Chat-Workspace (Presenter → UI)."""

    load_state: ChatWorkspaceLoadState
    connection: ChatConnectionStatus
    selected_chat_id: int | None
    filter_text: str
    chats: tuple[ChatListEntry, ...]
    messages: tuple[ChatMessageEntry, ...]
    models: tuple[ModelOptionEntry, ...]
    default_model_id: str | None
    project: ProjectContextEntry
    stream_phase: ChatStreamPhase
    streaming_message_index: int | None
    error: ChatErrorInfo | None = None
    details_panel: ChatDetailsPanelState | None = None


# --- Commands (UI → Presenter) ---


@dataclass(frozen=True, slots=True)
class SelectChatCommand:
    chat_id: int | None


@dataclass(frozen=True, slots=True)
class CreateChatCommand:
    title: str = "Neuer Chat"


@dataclass(frozen=True, slots=True)
class RenameChatCommand:
    chat_id: int
    title: str


@dataclass(frozen=True, slots=True)
class SendMessageCommand:
    text: str
    model_id: str | None = None


@dataclass(frozen=True, slots=True)
class StopGenerationCommand:
    pass


@dataclass(frozen=True, slots=True)
class LoadModelsCommand:
    pass


@dataclass(frozen=True, slots=True)
class SetChatFilterCommand:
    filter_text: str


ChatCommand = Union[
    SelectChatCommand,
    CreateChatCommand,
    RenameChatCommand,
    SendMessageCommand,
    StopGenerationCommand,
    LoadModelsCommand,
    SetChatFilterCommand,
]


# --- Partielle Zustandsaktualisierung (Presenter → UI) ---


@dataclass(frozen=True, slots=True)
class StreamChunkPatch:
    """
    Inkrementeller Stream-Block (nach Deduplizierung im Presenter).

    ``raw_chunk_meta`` ist optionaler, bereits gekürzter Meta-Dump für Debug/Inspector.
    """

    phase: ChatStreamPhase
    append_user_visible: str | None = None
    append_thinking: str | None = None
    target_message_index: int | None = None
    done: bool = False
    raw_chunk_meta: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ChatStatePatch:
    """
    Partielles Update. Felder mit Wert ``None`` bedeuten „keine Änderung“,
    außer ``clear_error: True`` setzt den Fehler zurück.

    Für Listen: ``None`` = unverändert; leere Tupel = bewusst leeren.
    """

    load_state: ChatWorkspaceLoadState | None = None
    connection: ChatConnectionStatus | None = None
    selected_chat_id: int | None = None
    clear_selected_chat: bool = False
    filter_text: str | None = None
    chats: tuple[ChatListEntry, ...] | None = None
    messages: tuple[ChatMessageEntry, ...] | None = None
    models: tuple[ModelOptionEntry, ...] | None = None
    default_model_id: str | None = None
    project: ProjectContextEntry | None = None
    stream_phase: ChatStreamPhase | None = None
    streaming_message_index: int | None = None
    stream_chunk: StreamChunkPatch | None = None
    error: ChatErrorInfo | None = None
    clear_error: bool = False
    details_panel: ChatDetailsPanelState | None = None


def merge_chat_state(base: ChatWorkspaceState, patch: ChatStatePatch) -> ChatWorkspaceState:
    """Reiner Funktions-Merge für Tests und Presenter-Hilfen."""
    err = None if patch.clear_error else (patch.error if patch.error is not None else base.error)
    sel = base.selected_chat_id
    if patch.clear_selected_chat:
        sel = None
    elif patch.selected_chat_id is not None:
        sel = patch.selected_chat_id
    return ChatWorkspaceState(
        load_state=patch.load_state or base.load_state,
        connection=patch.connection or base.connection,
        selected_chat_id=sel,
        filter_text=patch.filter_text if patch.filter_text is not None else base.filter_text,
        chats=patch.chats if patch.chats is not None else base.chats,
        messages=patch.messages if patch.messages is not None else base.messages,
        models=patch.models if patch.models is not None else base.models,
        default_model_id=(
            patch.default_model_id if patch.default_model_id is not None else base.default_model_id
        ),
        project=patch.project if patch.project is not None else base.project,
        stream_phase=patch.stream_phase or base.stream_phase,
        streaming_message_index=(
            patch.streaming_message_index
            if patch.streaming_message_index is not None
            else base.streaming_message_index
        ),
        error=err,
        details_panel=(
            patch.details_panel if patch.details_panel is not None else base.details_panel
        ),
    )


def chat_contract_to_json(obj: Any) -> Any:
    """Best-effort JSON-taugliche Struktur (Enums → value)."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [chat_contract_to_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: chat_contract_to_json(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        d = asdict(obj)
        return {k: chat_contract_to_json(v) for k, v in d.items()}
    raise TypeError(f"Unsupported contract type: {type(obj)!r}")


__all__ = [
    "ChatCommand",
    "ChatDetailsPanelState",
    "ChatErrorInfo",
    "ChatListEntry",
    "ChatMessageEntry",
    "ChatStatePatch",
    "ChatTopicOptionEntry",
    "ChatWorkspaceState",
    "CreateChatCommand",
    "LoadModelsCommand",
    "ModelOptionEntry",
    "ProjectContextEntry",
    "ProjectListRow",
    "RenameChatCommand",
    "SelectChatCommand",
    "SendMessageCommand",
    "SetChatFilterCommand",
    "StopGenerationCommand",
    "StreamChunkPatch",
    "chat_contract_to_json",
    "empty_chat_details_panel_state",
    "merge_chat_state",
]
