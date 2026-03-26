"""
Live-End-to-End-Trace: Roh-Chunk → Parser → Accumulator → UI-Bubble → Persistenz.

Aktivierung (eine reicht):
  export LDC_CHAT_STREAM_TRACE=1
oder weiterhin:
  export LDC_CHAT_CHUNK_FORENSIC=1

Logger: ``ldc.chat.stream_pipeline`` — auf INFO stellen, z. B.:

  export LDC_LOG_STREAM_PIPELINE=1   # optional: root-Logging in main anpassen
oder in Code::

  logging.getLogger("ldc.chat.stream_pipeline").setLevel(logging.INFO)

Jede Zeile ist mit ``[ldc_stream]`` markiert, damit grep einfach ist.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Mapping

_log = logging.getLogger("ldc.chat.stream_pipeline")

_PREVIEW = 160
_MAX_RAW_JSON = 6000


def trace_enabled() -> bool:
    a = os.environ.get("LDC_CHAT_STREAM_TRACE", "").strip().lower()
    b = os.environ.get("LDC_CHAT_CHUNK_FORENSIC", "").strip().lower()
    return a in ("1", "true", "yes") or b in ("1", "true", "yes")


def _pv(s: str | None) -> str:
    if not s:
        return ""
    t = s.replace("\r", "").replace("\n", "\\n")
    return t if len(t) <= _PREVIEW else t[:_PREVIEW] + "…"


def _json_chunk(chunk: Mapping[str, Any] | None) -> str:
    if chunk is None:
        return "null"
    try:
        s = json.dumps(dict(chunk), ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        s = repr(chunk)
    if len(s) > _MAX_RAW_JSON:
        return s[:_MAX_RAW_JSON] + "…(truncated)"
    return s


def _msg_field_summary(msg: Any, name: str = "message") -> str:
    if not isinstance(msg, Mapping):
        return f"{name}=<{type(msg).__name__}>"
    parts: list[str] = []
    for key in ("role", "content", "thinking", "reasoning"):
        v = msg.get(key)
        if v is None or v == "":
            continue
        if isinstance(v, str):
            parts.append(f"{key}:str(len={len(v)},pv={_pv(v)!r})")
        elif isinstance(v, list):
            parts.append(f"{key}:list(n={len(v)})")
        else:
            parts.append(f"{key}:{type(v).__name__}")
    return f"{name}={{{', '.join(parts)}}}" if parts else f"{name}={{}}"


def trace_raw_provider_chunk(seq: int, chunk: Mapping[str, Any] | None) -> None:
    """Schritt 1: ungefilterter Roh-Chunk (als JSON + Kurzsummary)."""
    if not trace_enabled() or chunk is None:
        return
    top = sorted(str(k) for k in chunk.keys())
    done = chunk.get("done")
    err = chunk.get("error")
    msg = chunk.get("message")
    line = (
        f"[ldc_stream] seq={seq} step=RAW top_keys={top} done={done!r} error={err!r} "
        + _msg_field_summary(msg)
    )
    _log.info("%s", line)
    _log.info("[ldc_stream] seq=%s step=RAW_JSON %s", seq, _json_chunk(chunk))


def trace_parser_output(
    seq: int,
    *,
    visible_len: int,
    visible_preview: str,
    visible_source: str,
    reasoning_piece_len: int,
    reasoning_preview: str,
    thinking_stripped_len: int,
    done: bool,
    parse_error: str | None,
) -> None:
    """Schritt 2: Ausgang parse_provider_chat_chunk / ParsedChatChunk."""
    if not trace_enabled():
        return
    _log.info(
        "[ldc_stream] seq=%s step=PARSED visible_len=%s source=%s visible_pv=%r "
        "reasoning_piece_len=%s reasoning_pv=%r think_strip_len=%s done=%s err=%r",
        seq,
        visible_len,
        visible_source,
        _pv(visible_preview),
        reasoning_piece_len,
        _pv(reasoning_preview),
        thinking_stripped_len,
        done,
        parse_error,
    )


def trace_accumulator_state(
    seq: int,
    *,
    phase: str,
    visible_total_len: int,
    visible_preview: str,
    reasoning_total_len: int,
    reasoning_preview: str,
    visible_changed: bool,
) -> None:
    """Schritt 3: Zustand Accumulator nach feed()."""
    if not trace_enabled():
        return
    _log.info(
        "[ldc_stream] seq=%s step=ACC phase=%s visible_total_len=%s visible_pv=%r "
        "reasoning_total_len=%s reasoning_pv=%r bubble_would_change=%s",
        seq,
        phase,
        visible_total_len,
        _pv(visible_preview),
        reasoning_total_len,
        _pv(reasoning_preview),
        visible_changed,
    )


def trace_ui_bubble_update(seq: int, *, text_len: int, text_preview: str, reason: str) -> None:
    """Schritt 4: Text, der an conversation_update_last_assistant geht."""
    if not trace_enabled():
        return
    _log.info(
        "[ldc_stream] seq=%s step=UI_BUBBLE reason=%s len=%s preview=%r",
        seq,
        reason,
        text_len,
        _pv(text_preview),
    )


def trace_post_finalize(*, text_len: int, text_preview: str, had_error: bool) -> None:
    """Nach final_assistant_message_for_persistence (vor Outcome-Status)."""
    if not trace_enabled():
        return
    _log.info(
        "[ldc_stream] step=POST_FINALIZE had_error=%s len=%s preview=%r",
        had_error,
        text_len,
        _pv(text_preview),
    )


def trace_persist_assistant(*, chat_id: int, text_len: int, text_preview: str) -> None:
    """Schritt 5: unmittelbar vor save_assistant_message."""
    if not trace_enabled():
        return
    _log.info(
        "[ldc_stream] step=PERSIST chat_id=%s len=%s preview=%r",
        chat_id,
        text_len,
        _pv(text_preview),
    )


def ensure_trace_logger_info() -> None:
    """Sorgt dafür, dass Trace-Zeilen ohne manuelles Logging-Setup sichtbar sind."""
    if not trace_enabled():
        return
    if _log.level > logging.INFO:
        _log.setLevel(logging.INFO)
    if not _log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
        _log.addHandler(h)
        _log.propagate = False
