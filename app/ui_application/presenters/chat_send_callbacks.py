"""
Callbacks für den Chat-Send-Pipeline — keine Qt-Typen, nur Callable.

Die ``ChatWorkspace``-Implementierung füllt diese Hooks mit Widget-Zugriffen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class ChatSendCallbacks:
    conversation_add_user: Callable[[str], None]
    conversation_scroll_bottom: Callable[[], None]
    conversation_add_placeholder: Callable[[str], None]
    conversation_update_last_assistant: Callable[[str], None]
    conversation_set_last_completion: Callable[[str | None], None]
    conversation_finalize_streaming: Callable[[], None]
    input_set_sending: Callable[[bool], None]
    details_set_invocation_view: Callable[[object], None]
    refresh_session_explorer: Callable[[], None]
    set_session_explorer_current: Callable[[int], None]
    refresh_context_bar: Callable[[], None]
    refresh_details_panel: Callable[[], None]
    refresh_inspector: Callable[[], None]
    show_error_inline: Callable[[str], None]
    notify_send_session_completed: Callable[[ChatSendSession], None] | None = None


@dataclass
class ChatSendSession:
    """Mutable Session-ID für den Send-Lauf (Presenter aktualisiert bei Neuanlage)."""

    chat_id: int | None
