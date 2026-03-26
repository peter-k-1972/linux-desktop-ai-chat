"""
Kompatibilitäts-Shim: Chat-Stream-Assembler liegt in :mod:`app.chat.stream_assembler`.

Neue Imports bitte direkt aus ``app.chat.stream_assembler``; dieses Modul bleibt
für bestehende Presenter-/Test-Pfade erhalten.
"""

from __future__ import annotations

from app.chat.stream_assembler import (
    ChatStreamAccumulator,
    ParsedChatChunk,
    StreamPieceSource,
    absorb_incremental_or_cumulative,
    append_stream_piece,
    dedupe_overlap_append,
    extract_stream_display,
    final_assistant_message_for_persistence,
    parse_provider_chat_chunk,
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
