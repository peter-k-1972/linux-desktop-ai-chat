"""
Legacy GUI-Widgets – verortet aus app-Root.

Diese Module sind deprecated. Sie werden von der Legacy-GUI (main.py, run_legacy_gui.py)
und Tests genutzt. Standard-GUI nutzt gui/domains/.
"""

from app.gui.legacy.chat_widget import (
    ChatWidget,
    is_placeholder_or_invalid_assistant_message,
    finalize_stream_response,
    _extract_chunk_parts,
)
from app.gui.legacy.sidebar_widget import SidebarWidget
from app.gui.legacy.project_chat_list_widget import ProjectChatListWidget
from app.gui.legacy.message_widget import MessageWidget
from app.gui.legacy.file_explorer_widget import FileExplorerWidget

__all__ = [
    "ChatWidget",
    "SidebarWidget",
    "ProjectChatListWidget",
    "MessageWidget",
    "FileExplorerWidget",
    "is_placeholder_or_invalid_assistant_message",
    "finalize_stream_response",
    "_extract_chunk_parts",
]
