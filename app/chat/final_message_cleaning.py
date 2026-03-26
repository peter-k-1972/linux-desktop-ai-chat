"""
Finaler sichtbarer Assistant-Text: Bereinigung eingebetteter Denk-Markup.

Segment 7 (Ergaenzung): reine String-Transformation, kein Logging, keine Forensik.
"""

from __future__ import annotations

import re


def _think_pair(open_tag: str, close_tag: str) -> re.Pattern[str]:
    return re.compile(
        re.escape(open_tag) + r"[\s\S]*?" + re.escape(close_tag),
        re.IGNORECASE,
    )


_THINK_BLOCK_RES = (
    _think_pair("<think>", "</think>"),
    _think_pair("<reasoning>", "</reasoning>"),
)


def strip_embedded_think_blocks(visible: str) -> str:
    """
    Entfernt eingebettete Denk-Blöcke aus dem **fertigen** sichtbaren Assistant-Text.

    Wenn das Modell Denken und Antwort in *einem* content-String ausliefert,
    bleibt nach dem Strip die eigentliche Antwort erhalten. Reasoning, das
    bereits im separaten ``thinking``-Feld ankam, wird davon nicht berührt
    (liegt nicht in diesem String).
    """
    if not visible:
        return visible
    out = visible
    for rx in _THINK_BLOCK_RES:
        out = rx.sub("", out)
    return out.strip()
