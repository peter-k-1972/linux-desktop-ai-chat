"""Gemeinsame UI-Enums (serialisierbar, Qt-frei)."""

from __future__ import annotations

from enum import Enum


class ChatWorkspaceLoadState(str, Enum):
    """Grobzustand des Chat-Workspaces (ohne Threading/Qt)."""

    IDLE = "idle"
    LOADING_CHATS = "loading_chats"
    LOADING_MESSAGES = "loading_messages"
    STREAMING = "streaming"
    ERROR = "error"


class ChatStreamPhase(str, Enum):
    """Phase eines laufenden Assistant-Streams (Anzeige/UX)."""

    IDLE = "idle"
    THINKING = "thinking"
    CONTENT = "content"
    TOOL = "tool"
    DONE = "done"


class ChatConnectionStatus(str, Enum):
    """Provider-/Modell-Erreichbarkeit (vereinfachtes UI-Modell)."""

    UNKNOWN = "unknown"
    CHECKING = "checking"
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class FallbackPolicy(str, Enum):
    """Wie ein Theme-Loader fehlende Packs/Versionen behandeln soll."""

    USE_BUILTIN_LIGHT_DEFAULT = "use_builtin_light_default"
    REJECT = "reject"
    USE_PARENT_THEME_ONLY = "use_parent_theme_only"


__all__ = [
    "ChatConnectionStatus",
    "ChatStreamPhase",
    "ChatWorkspaceLoadState",
    "FallbackPolicy",
]
