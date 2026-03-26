"""
Kompatibilitäts-Fassade: Re-Exports der Chat-Stream-Segmente.

Implementierung:
- :mod:`app.chat.provider_stream_normalize` — Parsing / :class:`ParsedChatChunk`
- :mod:`app.chat.stream_accumulator` — :class:`ChatStreamAccumulator`, Absorb-Helfer
- :mod:`app.chat.final_assistant_message` — Persistenz-Finale

Von außen weiterhin über ``app.ui_application.presenters.chat_stream_assembler`` (Shim).
"""

from __future__ import annotations

from app.chat.final_assistant_message import final_assistant_message_for_persistence
from app.chat.provider_stream_normalize import (
    ParsedChatChunk,
    StreamPieceSource,
    extract_stream_display,
    parse_provider_chat_chunk,
)
from app.chat.stream_accumulator import (
    ChatStreamAccumulator,
    absorb_incremental_or_cumulative,
    append_stream_piece,
    dedupe_overlap_append,
)

__all__ = [
    "ChatStreamAccumulator",
    "ParsedChatChunk",
    "StreamPieceSource",
    "absorb_incremental_or_cumulative",
    "append_stream_piece",
    "dedupe_overlap_append",
    "extract_stream_display",
    "final_assistant_message_for_persistence",
    "parse_provider_chat_chunk",
]
