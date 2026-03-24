"""
Stream-Chunk-Verarbeitung für Chat-Anzeige (Qt-frei, kein I/O).

Ausgelagert aus ``ChatWorkspace`` — Widget/Presenter rufen nur noch diese Funktionen.
"""

from __future__ import annotations

from typing import Any


def append_stream_piece(full: str, piece: str) -> str:
    """
    Hängt einen Stream-Teil an und entfernt maximales Suffix/Präfix-Overlap.

    Verhindert Duplikate wenn späterer ``message.content`` den bereits über
    ``thinking`` gezeigten Text wiederholt, oder wenn ein Provider kumulative
    statt strikt inkrementelle Blöcke sendet.
    """
    if not piece:
        return full
    if not full:
        return piece
    max_k = min(len(full), len(piece))
    for k in range(max_k, 0, -1):
        if full.endswith(piece[:k]):
            return full + piece[k:]
    return full + piece


def extract_stream_display(chunk: dict[str, Any] | None) -> tuple[str, str, str | None, bool]:
    """
    Extrahiert Anzeige-Text, thinking, error, done aus einem Stream-Chunk.

    Wenn ``message.content`` leer ist, aber ``message.thinking`` nicht, wird
    ``thinking`` als Anzeige-Text verwendet (z. B. Modelle mit getrenntem
    Thinking-Stream).
    """
    if chunk is None or not isinstance(chunk, dict):
        return ("", "", None, False)
    if "error" in chunk:
        return ("", "", str(chunk.get("error", "")), bool(chunk.get("done", False)))
    msg = chunk.get("message") or {}
    raw_c = msg.get("content")
    if raw_c is None:
        raw_c = ""
    if isinstance(raw_c, str):
        content_str = raw_c
    else:
        content_str = str(raw_c)
    th_raw = msg.get("thinking") or ""
    if not isinstance(th_raw, str):
        th_raw = str(th_raw) if th_raw is not None else ""
    thinking = th_raw.strip()
    if content_str.strip():
        out = content_str
    elif thinking:
        out = th_raw
    else:
        out = ""
    done = bool(chunk.get("done", False))
    return (out, thinking, None, done)
