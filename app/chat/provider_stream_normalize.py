"""
Segment 2/3: Roh-Provider-Chunk (dict) -> kanonisches :class:`ParsedChatChunk`.

Qt-frei, keine Akkumulation, keine Persistenz-Finalisierung.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

StreamPieceSource = Literal["content", "none"]

# Strukturierte message-/delta-``content``-Listen: ``type``-Werte, die zum Reasoning-Kanal gehoeren.
# Nur Eintraege ergaenzen, die in Provider-/Gateway-Dokus oder diesem Repo als CoT/Reasoning belegt sind
# (keine Spekulation z. B. ``analysis``, ``cot``, ``chain_of_thought`` — kollidieren leicht mit sichtbarem Text).
STRUCTURED_REASONING_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "reasoning",
        "thinking",
        "think",
        "thought",
        "redacted_reasoning",
        "redacted_thinking",
        "reasoning_content",
    }
)


@dataclass(frozen=True)
class ParsedChatChunk:
    """
    Normalisiertes Einzelstück aus einem Provider-Stream-Chunk.

    ``reasoning_raw_piece`` aggregiert Denken aus thinking/reasoning-Feldern und
    aus Content-Listeneinträgen vom Typ ``reasoning``/``thinking``.
    ``visible_piece`` ist ausschließlich Antwortfragmente aus Content-Pfaden
    (delta/message/output_text/top-level content), niemals aus Thinking-Feldern.
    """

    reasoning_raw_piece: str
    thinking_stripped: str
    visible_piece: str
    visible_source: StreamPieceSource
    error: str | None
    done: bool


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)


def _split_structured_content(raw: object) -> tuple[str, str]:
    """
    Zerlegt ``content``-Rohwert in (sichtbarer_text, reasoning_text) für diesen Chunk.

    - String → (raw, "").
    - Liste von Dicts mit ``type`` reasoning/thinking/... → reasoning; sonst Textfelder.
    - Sonst → (str(raw), "") — nur für nicht-strukturierte Einzelwerte.
    """
    if raw is None:
        return "", ""
    if isinstance(raw, str):
        return raw, ""
    if isinstance(raw, list):
        vis: list[str] = []
        reas: list[str] = []
        for item in raw:
            if isinstance(item, dict):
                typ = (item.get("type") or "").lower()
                text = item.get("text")
                if text is None:
                    text = item.get("content")
                if text is None:
                    text = item.get("value")
                if not isinstance(text, str):
                    text = _as_str(text)
                if typ in STRUCTURED_REASONING_CONTENT_TYPES:
                    reas.append(text)
                else:
                    vis.append(text)
            else:
                vis.append(_as_str(item))
        return "".join(vis), "".join(reas)
    return _as_str(raw), ""


def _visible_from_raw_content(raw: object) -> str | None:
    """Erstes nicht-leeres sichtbares Fragment aus einem Content-Feld, sonst None."""
    vis, _ = _split_structured_content(raw)
    if vis.strip():
        return vis
    return None


def _visible_piece_priority(chunk: dict[str, Any]) -> tuple[str, StreamPieceSource]:
    """
    Sichtbarer Text nur aus (Priorität):
    1. choices[0].delta.content
    2. choices[0].message.content
    3. message.content
    4. output_text (String)
    5. content (String oder Liste)
    """
    choices = chunk.get("choices")
    if isinstance(choices, list) and choices:
        c0 = choices[0]
        if isinstance(c0, dict):
            d = c0.get("delta")
            if isinstance(d, dict):
                v = _visible_from_raw_content(d.get("content"))
                if v is not None:
                    return v, "content"
            m = c0.get("message")
            if isinstance(m, dict):
                v = _visible_from_raw_content(m.get("content"))
                if v is not None:
                    return v, "content"
    msg = chunk.get("message")
    if isinstance(msg, dict):
        v = _visible_from_raw_content(msg.get("content"))
        if v is not None:
            return v, "content"
    ot = chunk.get("output_text")
    if isinstance(ot, str) and ot.strip():
        return ot, "content"
    v = _visible_from_raw_content(chunk.get("content"))
    if v is not None:
        return v, "content"
    return "", "none"


def _collect_reasoning_raw_piece(chunk: dict[str, Any]) -> str:
    """Thinking/Reasoning aus allen unterstützten Feldern + Reasoning-Teile aus Content-Listen."""
    parts: list[str] = []
    choices = chunk.get("choices")
    c0 = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None

    def push(s: object) -> None:
        t = _as_str(s)
        if t.strip():
            parts.append(t)

    if isinstance(c0, dict):
        d = c0.get("delta")
        if isinstance(d, dict):
            push(d.get("reasoning_content"))
            push(d.get("reasoning"))
            push(d.get("thinking"))
        m = c0.get("message")
        if isinstance(m, dict):
            push(m.get("thinking"))
            push(m.get("reasoning"))
    msg = chunk.get("message")
    if isinstance(msg, dict):
        push(msg.get("thinking"))
        push(msg.get("reasoning"))
    push(chunk.get("thinking"))
    push(chunk.get("reasoning"))

    def push_list_reas(raw: object) -> None:
        _, reas = _split_structured_content(raw)
        if reas.strip():
            parts.append(reas)

    if isinstance(c0, dict):
        d = c0.get("delta")
        if isinstance(d, dict):
            push_list_reas(d.get("content"))
        m = c0.get("message")
        if isinstance(m, dict):
            push_list_reas(m.get("content"))
    if isinstance(msg, dict):
        push_list_reas(msg.get("content"))
    push_list_reas(chunk.get("content"))

    return "".join(parts)


def parse_provider_chat_chunk(chunk: dict[str, Any] | None) -> ParsedChatChunk:
    """
    Einheitliche Parser-Schicht: Provider-Dict → :class:`ParsedChatChunk`.

    Sichtbarer Text ausschließlich über Content-Pfade (siehe :func:`_visible_piece_priority`).
    Kein Fallback sichtbar ← thinking/reasoning.
    """
    if chunk is None or not isinstance(chunk, dict):
        return ParsedChatChunk("", "", "", "none", None, False)
    # Nur echte Fehler: Key allein reicht nicht (z. B. "error": null aus generierten Clients).
    err_val = chunk.get("error")
    if err_val not in (None, "", False):
        return ParsedChatChunk(
            "",
            "",
            "",
            "none",
            str(err_val),
            bool(chunk.get("done", False)),
        )

    reasoning_merged = _collect_reasoning_raw_piece(chunk)
    thinking_stripped = reasoning_merged.strip()
    reasoning_raw_piece = reasoning_merged if thinking_stripped else ""

    visible_piece, visible_source = _visible_piece_priority(chunk)

    return ParsedChatChunk(
        reasoning_raw_piece=reasoning_raw_piece,
        thinking_stripped=thinking_stripped,
        visible_piece=visible_piece,
        visible_source=visible_source,
        error=None,
        done=bool(chunk.get("done", False)),
    )


def extract_stream_display(
    chunk: dict[str, Any] | None,
) -> tuple[str, str, str | None, bool, StreamPieceSource]:
    p = parse_provider_chat_chunk(chunk)
    if p.error is not None:
        return ("", "", p.error, p.done, "none")
    return (p.visible_piece, p.thinking_stripped, None, p.done, p.visible_source)
