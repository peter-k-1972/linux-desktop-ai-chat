"""
Segment 6: Live-Akkumulation von sichtbarem Text und Reasoning aus :func:`parse_provider_chat_chunk`.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Literal

from app.chat.provider_stream_normalize import parse_provider_chat_chunk

_log = logging.getLogger(__name__)


def absorb_incremental_or_cumulative(buffer: str, piece: str) -> str:
    """Gleiche Zusammenführung wie für sichtbaren Stream-Text im :class:`ChatStreamAccumulator`."""
    if not piece:
        return buffer
    if not buffer:
        return piece
    if len(piece) >= len(buffer) and piece.startswith(buffer):
        return piece
    return buffer + piece


def dedupe_overlap_append(full: str, piece: str, *, min_overlap: int = 1) -> str:
    if not piece:
        return full
    if not full:
        return piece
    max_k = min(len(full), len(piece))
    low = max(0, min_overlap - 1)
    for k in range(max_k, low, -1):
        if full.endswith(piece[:k]):
            return full + piece[k:]
    return full + piece


def append_stream_piece(full: str, piece: str) -> str:
    return dedupe_overlap_append(full, piece, min_overlap=1)


class ChatStreamAccumulator:
    __slots__ = ("_reasoning_text", "_visible", "phase", "_chunk_seq", "_last_feed_seq")

    def __init__(self) -> None:
        self._visible: str = ""
        self._reasoning_text: str = ""
        self.phase: Literal["start", "content"] = "start"
        self._chunk_seq: int = 0
        self._last_feed_seq: int = 0

    @property
    def full(self) -> str:
        return self._visible

    @property
    def visible_assistant_text(self) -> str:
        return self._visible

    @property
    def reasoning_text(self) -> str:
        return self._reasoning_text

    @property
    def trace_seq_for_next_chunk(self) -> int:
        """Nächste laufende Chunk-Nummer (für RAW-Trace vor feed)."""
        return self._chunk_seq + 1

    @property
    def last_feed_seq(self) -> int:
        """Chunk-Nummer des zuletzt verarbeiteten feed()-Aufrufs."""
        return self._last_feed_seq

    def _trace_accumulator(self, seq: int, visible_changed: bool) -> None:
        from app.chat.stream_pipeline_trace import trace_accumulator_state, trace_enabled

        if not trace_enabled():
            return
        trace_accumulator_state(
            seq,
            phase=self.phase,
            visible_total_len=len(self._visible),
            visible_preview=self._visible,
            reasoning_total_len=len(self._reasoning_text),
            reasoning_preview=self._reasoning_text,
            visible_changed=visible_changed,
        )

    def feed(self, chunk: dict[str, Any] | None) -> tuple[str | None, bool, bool]:
        p = parse_provider_chat_chunk(chunk)
        self._chunk_seq += 1
        seq = self._chunk_seq
        self._last_feed_seq = seq

        from app.chat.stream_pipeline_trace import trace_enabled, trace_parser_output

        if trace_enabled():
            trace_parser_output(
                seq,
                visible_len=len(p.visible_piece or ""),
                visible_preview=p.visible_piece or "",
                visible_source=p.visible_source,
                reasoning_piece_len=len(p.reasoning_raw_piece or ""),
                reasoning_preview=p.reasoning_raw_piece or "",
                thinking_stripped_len=len(p.thinking_stripped or ""),
                done=p.done,
                parse_error=p.error,
            )

        _stream_debug = os.environ.get("LDC_CHAT_STREAM_DEBUG", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if os.environ.get("LDC_CHAT_CHUNK_FORENSIC", "").strip().lower() in ("1", "true", "yes"):
            from app.chat.provider_chunk_forensics import log_provider_chunk_and_parse

            if isinstance(chunk, dict):
                log_provider_chunk_and_parse(seq, chunk, p, self)

        if p.error is not None:
            self._trace_accumulator(seq, False)
            if _stream_debug:
                _log.info(
                    "chat_stream seq=%s visible_piece_len=0 visible_total_len=%s reasoning_total_len=%s "
                    "phase=%s err=%s done=%s",
                    seq,
                    len(self._visible),
                    len(self._reasoning_text),
                    self.phase,
                    p.error,
                    p.done,
                )
            return p.error, p.done, False

        if p.reasoning_raw_piece:
            self._reasoning_text = absorb_incremental_or_cumulative(
                self._reasoning_text, p.reasoning_raw_piece
            )

        visible_changed = False
        if p.visible_piece:
            before = self._visible
            self._visible = absorb_incremental_or_cumulative(self._visible, p.visible_piece)
            visible_changed = self._visible != before
            if self.phase == "start":
                self.phase = "content"

        self._trace_accumulator(seq, visible_changed)
        if _stream_debug:
            _log.info(
                "chat_stream seq=%s visible_piece_len=%s visible_total_len=%s reasoning_total_len=%s "
                "phase=%s src=%s visible_changed=%s done=%s",
                seq,
                len(p.visible_piece or ""),
                len(self._visible),
                len(self._reasoning_text),
                self.phase,
                p.visible_source,
                visible_changed,
                p.done,
            )
        return None, p.done, visible_changed
