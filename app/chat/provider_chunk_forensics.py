"""
Optionale Live-Forensik für Chat-Stream-Chunks (Provider → Parser → Accumulator).

Aktivierung: Umgebungsvariable ``LDC_CHAT_CHUNK_FORENSIC=1`` (oder ``true``/``yes``).

Loggt strukturiert über Logger ``app.chat.provider_chunk_forensics`` — keine Secrets,
Inhalte nur als Länge + Preview (erste 120 Zeichen), Roh-JSON gekappt.

``strip_embedded_think_blocks`` wird hier nur noch re-exportiert (kanonisch:
:mod:`app.chat.final_message_cleaning`).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Mapping

# Rückwärtskompatibilität: früher hier definiert; kanonisch in final_message_cleaning.
from app.chat.final_message_cleaning import strip_embedded_think_blocks

_log = logging.getLogger(__name__)

_PREVIEW = 120
_MAX_JSON = 4000


def _enabled() -> bool:
    return os.environ.get("LDC_CHAT_CHUNK_FORENSIC", "").strip().lower() in ("1", "true", "yes")


def _preview(s: str | None) -> str:
    if s is None:
        return ""
    t = s.replace("\n", "\\n")
    if len(t) <= _PREVIEW:
        return t
    return t[:_PREVIEW] + "…"


def _type_name(v: Any) -> str:
    if v is None:
        return "null"
    return type(v).__name__


def _summarize_mapping(prefix: str, d: Mapping[str, Any], depth: int = 0) -> None:
    if depth > 4 or not isinstance(d, Mapping):
        return
    for k in sorted(d.keys(), key=lambda x: str(x)):
        v = d[k]
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, Mapping):
            _log.info("  %s → (%s keys)", key, len(v))
            if k in ("message", "delta", "choices") or depth == 0:
                _summarize_mapping(key, v, depth + 1)
        elif isinstance(v, list):
            _log.info("  %s → list[len=%s] elem0=%s", key, len(v), _type_name(v[0]) if v else "—")
        else:
            if isinstance(v, str):
                _log.info("  %s str len=%s preview=%r", key, len(v), _preview(v))
            else:
                _log.info("  %s %s repr=%r", key, _type_name(v), _preview(repr(v))[:120])


def log_provider_chunk_and_parse(
    chunk_index: int,
    raw_chunk: dict[str, Any] | None,
    parsed: Any,
    acc: Any,
) -> None:
    if not _enabled() or raw_chunk is None:
        return
    try:
        raw_json = json.dumps(raw_chunk, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        raw_json = repr(raw_chunk)
    if len(raw_json) > _MAX_JSON:
        raw_json = raw_json[:_MAX_JSON] + "…(truncated)"

    _log.info(
        "=== CHUNK_FORENSIC #%s done=%s === raw_json(len=%s)=%s",
        chunk_index,
        parsed.done,
        len(raw_json),
        raw_json,
    )
    _summarize_mapping("", raw_chunk)

    _log.info(
        "PARSED reasoning_raw_piece len=%s preview=%r | thinking_stripped len=%s | "
        "visible_piece len=%s preview=%r | visible_source=%s | err=%s",
        len(parsed.reasoning_raw_piece),
        _preview(parsed.reasoning_raw_piece),
        len(parsed.thinking_stripped),
        len(parsed.visible_piece),
        _preview(parsed.visible_piece),
        parsed.visible_source,
        parsed.error,
    )
    _log.info(
        "ACCUMULATOR reasoning_text len=%s | visible_assistant_text len=%s | phase=%s",
        len(acc.reasoning_text),
        len(acc.visible_assistant_text),
        getattr(acc, "phase", "?"),
    )


__all__ = [
    "log_provider_chunk_and_parse",
    "strip_embedded_think_blocks",
]
