"""
Normalisierung: Zeilenenden, Tabs, optionale ASCII-Absatz-Promotion mit Dedent.
"""

from __future__ import annotations

from app.gui.shared.markdown.markdown_types import (
    AsciiBlock,
    MarkdownDocument,
    ParagraphBlock,
)
from app.gui.shared.markdown.markdown_rules import paragraph_looks_like_ascii_art


def normalize_markdown(text: str) -> str:
    """
    Stabilisiert Eingabetext für den Parser:
    - CRLF/CR → LF
    - Tabs → Leerzeichen (4er-Stops via expandtabs)
    """
    if not text:
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(ln.expandtabs(4) for ln in t.split("\n"))


def normalize_source(text: str) -> str:
    """Abwärtskompatibel: identisch zu normalize_markdown."""
    return normalize_markdown(text)


def _dedent_common_minimum(lines: list[str]) -> list[str]:
    """Entfernt gemeinsame führende Leerzeichen bei nicht-leeren Zeilen (ASCII-Blöcke)."""
    non_empty = [ln for ln in lines if ln.strip()]
    if len(non_empty) < 2:
        return lines
    indents: list[int] = []
    for ln in non_empty:
        stripped = ln.lstrip(" ")
        if not stripped:
            continue
        indents.append(len(ln) - len(stripped))
    if not indents:
        return lines
    m = min(indents)
    if m <= 0:
        return lines
    out: list[str] = []
    for ln in lines:
        if not ln.strip():
            out.append("")
        elif len(ln) >= m and ln[:m] == " " * m:
            out.append(ln[m:])
        else:
            out.append(ln)
    return out


def promote_ascii_paragraphs(document: MarkdownDocument) -> MarkdownDocument:
    """
    Ersetzt mehrzeilige Absätze mit ASCII-Heuristik durch AsciiBlock (Monospace).
    Wendet gemeinsames Dedent an, um uneinheitliche Einrückung zu stabilisieren.
    """
    out: list = []
    for b in document.blocks:
        if isinstance(b, ParagraphBlock) and paragraph_looks_like_ascii_art(b.lines):
            dedented = _dedent_common_minimum(list(b.lines))
            body = "\n".join(dedented)
            out.append(AsciiBlock(body=body))
        else:
            out.append(b)
    return MarkdownDocument(blocks=out, source_normalized=document.source_normalized)
