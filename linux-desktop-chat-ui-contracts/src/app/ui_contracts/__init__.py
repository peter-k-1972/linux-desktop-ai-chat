"""
Qt-freie UI-Verträge (DTOs, Commands, Events).

Dieses Paket importiert weder PySide6 noch app.services.

Öffentliche API: Paket-Root (Chat, gemeinsame Enums/Events, ``SettingsErrorInfo``, siehe
``__all__``) und ``app.ui_contracts.workspaces.<modul>`` für übrige Workspaces — siehe
``docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md`` und
``docs/architecture/PACKAGE_UI_CONTRACTS_CUT_READY.md``.
"""

from app.ui_contracts.common.enums import (
    ChatConnectionStatus,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
    FallbackPolicy,
)
from app.ui_contracts.common.errors import SettingsErrorInfo
from app.ui_contracts.common.events import ChatUiEvent
from app.ui_contracts.workspaces.chat import (
    ChatCommand,
    ChatDetailsPanelState,
    ChatErrorInfo,
    ChatListEntry,
    ChatMessageEntry,
    ChatStatePatch,
    ChatTopicOptionEntry,
    ChatWorkspaceState,
    CreateChatCommand,
    LoadModelsCommand,
    ModelOptionEntry,
    ProjectContextEntry,
    ProjectListRow,
    RenameChatCommand,
    SelectChatCommand,
    SendMessageCommand,
    SetChatFilterCommand,
    StopGenerationCommand,
    StreamChunkPatch,
)

__all__ = [
    "ChatCommand",
    "ChatConnectionStatus",
    "ChatDetailsPanelState",
    "ChatErrorInfo",
    "ChatListEntry",
    "ChatMessageEntry",
    "ChatStatePatch",
    "ChatStreamPhase",
    "ChatTopicOptionEntry",
    "ChatUiEvent",
    "ChatWorkspaceLoadState",
    "ChatWorkspaceState",
    "CreateChatCommand",
    "FallbackPolicy",
    "LoadModelsCommand",
    "ModelOptionEntry",
    "ProjectContextEntry",
    "ProjectListRow",
    "RenameChatCommand",
    "SelectChatCommand",
    "SendMessageCommand",
    "SettingsErrorInfo",
    "SetChatFilterCommand",
    "StopGenerationCommand",
    "StreamChunkPatch",
]
