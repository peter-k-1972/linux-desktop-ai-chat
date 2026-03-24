"""
Qt-freie UI-Verträge (DTOs, Commands, Events).

Dieses Paket importiert weder PySide6 noch app.services.
"""

from app.ui_contracts.common.enums import (
    ChatConnectionStatus,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
    FallbackPolicy,
)
from app.ui_contracts.common.events import ChatUiEvent
from app.ui_contracts.workspaces.chat import (
    ChatCommand,
    ChatErrorInfo,
    ChatListEntry,
    ChatMessageEntry,
    ChatStatePatch,
    ChatWorkspaceState,
    CreateChatCommand,
    LoadModelsCommand,
    RenameChatCommand,
    SelectChatCommand,
    SendMessageCommand,
    StopGenerationCommand,
    StreamChunkPatch,
)

__all__ = [
    "ChatCommand",
    "ChatConnectionStatus",
    "ChatErrorInfo",
    "ChatListEntry",
    "ChatMessageEntry",
    "ChatStatePatch",
    "ChatStreamPhase",
    "ChatUiEvent",
    "ChatWorkspaceLoadState",
    "ChatWorkspaceState",
    "CreateChatCommand",
    "FallbackPolicy",
    "LoadModelsCommand",
    "RenameChatCommand",
    "SelectChatCommand",
    "SendMessageCommand",
    "StopGenerationCommand",
    "StreamChunkPatch",
]
