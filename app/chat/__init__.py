"""
Chat-Domain: Completion-Status, Heuristiken, Kontext, Metadaten.

Enthält u. a.:
- completion_status: Modell für Antwortvollständigkeit
- completion_heuristics: Heuristische Erkennung unvollständiger Antworten
- context: ChatContext und Kontext-Injection für Modell-Prompts
- provider_stream_normalize, stream_accumulator, final_assistant_message, stream_assembler,
  stream_consume: Chat-Stream-Segmente (siehe Module)
"""

from app.chat.completion_status import (
    CompletionStatus,
    completion_status_from_db,
    completion_status_to_db,
    is_incomplete,
)
from app.chat.completion_heuristics import (
    assess_completion_heuristic,
    get_heuristic_flags,
)
from app.chat.context import (
    ChatContext,
    ChatRequestContext,
    build_chat_context,
    inject_chat_context_into_messages,
)

__all__ = [
    "CompletionStatus",
    "completion_status_from_db",
    "completion_status_to_db",
    "is_incomplete",
    "assess_completion_heuristic",
    "get_heuristic_flags",
    "ChatContext",
    "ChatRequestContext",
    "build_chat_context",
    "inject_chat_context_into_messages",
]
