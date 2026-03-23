"""
Erkennung: Fließtext-Markdown vs. Code vs. ASCII-/Monospace-Pflicht vs. reiner Text.

ASCII: lieber zu oft als Monospace markieren als Diagramme zu zerstören.
"""

from __future__ import annotations

import re

from app.gui.shared.markdown.markdown_types import (
    AsciiBlock,
    Block,
    BlockquoteBlock,
    CodeFenceBlock,
    HeadingBlock,
    HrBlock,
    IndentedCodeBlock,
    ListBlock,
    ContentProfile,
    MarkdownDocument,
    ParagraphBlock,
    RenderMode,
    TableBlock,
)

_MARKDOWN_HINT = re.compile(
    r"^#{1,6}\s|^\s*[-*+]\s|^\s*\d+\.\s|```|\[.+?\]\(.+?\)|\*\*.+?\*\*|`[^`]+`",
    re.MULTILINE,
)
_BOX_LINE = re.compile(r"^[\s\-+|.:=#oO/\\]{6,}$")
_TREE_OR_TABLE = re.compile(r"^[\s│├└┌┐┘┬┴┼─]+\S")
_STRUCTURE_CHARS = frozenset("|+-/\\_=<>[]()")
_CLI_LINE = re.compile(
    r"^\s*(\$\s|#\s|>\s|C:\\|INFO|WARN|ERROR|ERR!|Traceback|at\s+\w|^\[\w+\]|docker\s|kubectl\s|npm\s|pip\s)",
    re.IGNORECASE,
)


def classify_source(text: str) -> ContentProfile:
    """
    Grobe Klassifikation vor dem Block-Parsing (deterministisch).
    """
    t = text.strip("\n")
    if not t.strip():
        return ContentProfile.RAW_PLAIN

    lines = t.split("\n")
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return ContentProfile.RAW_PLAIN

    if not _MARKDOWN_HINT.search(t):
        if _ascii_monospace_score(non_empty) >= 0.28:
            return ContentProfile.ASCII_MONOSPACE
        return ContentProfile.RAW_PLAIN

    return ContentProfile.MARKDOWN_FLOW


def _structure_density(s: str) -> float:
    if not s:
        return 0.0
    hits = sum(1 for c in s if c in _STRUCTURE_CHARS or c in "│├└┌┐┘─")
    return hits / len(s)


def _avg_structure_density(lines: list[str]) -> float:
    ne = [ln for ln in lines if ln.strip()]
    if not ne:
        return 0.0
    return sum(_structure_density(ln) for ln in ne) / len(ne)


def _common_indent_ok(lines: list[str]) -> bool:
    """Mehrere nicht-leere Zeilen mit gleicher Einrückung (≥2 Spaces)."""
    ne = [ln for ln in lines if ln.strip()]
    if len(ne) < 2:
        return False
    indents = [len(ln) - len(ln.lstrip(" ")) for ln in ne]
    return len(set(indents)) == 1 and indents[0] >= 2


def _ascii_monospace_score(lines: list[str]) -> float:
    """Anteil der Zeilen, die wie Diagramm/CLI aussehen (0..1)."""
    if not lines:
        return 0.0
    hits = 0
    for ln in lines:
        s = ln.rstrip()
        if not s:
            continue
        if _CLI_LINE.match(s):
            hits += 1
            continue
        if _TREE_OR_TABLE.match(s):
            hits += 1
            continue
        boxish = sum(1 for c in s if c in "+-|") / max(len(s), 1)
        if boxish >= 0.18 and len(s) >= 6:
            hits += 1
            continue
        if _structure_density(s) >= 0.12 and len(s) >= 10:
            hits += 1
            continue
        if _BOX_LINE.match(s):
            hits += 1
            continue
        alnum = sum(c.isalnum() for c in s)
        if len(s) >= 10 and alnum / len(s) < 0.38:
            hits += 1
    return hits / len(lines)


def paragraph_looks_like_ascii_art(lines: list[str]) -> bool:
    """
    Absatz ohne typische Markdown-Hints → Monospace-Block, wenn ASCII/CLI wahrscheinlich.
    Schwellen bewusst niedrig (False-Positives ok).
    """
    if not lines:
        return False
    joined = "\n".join(lines)
    if _MARKDOWN_HINT.search(joined):
        return False
    ne = [ln for ln in lines if ln.strip()]
    if not ne:
        return False

    if len(ne) >= 2:
        if _common_indent_ok(ne) and _avg_structure_density(ne) >= 0.05:
            return True
        if _ascii_monospace_score(ne) >= 0.28:
            return True

    if len(ne) == 1:
        s = ne[0]
        if _CLI_LINE.match(s):
            return True
        if _structure_density(s) >= 0.18 and len(s) >= 14:
            return True
        if sum(1 for c in s if c == "|") >= 4 and _structure_density(s) >= 0.1:
            return True

    return _ascii_monospace_score(ne) >= 0.45


def infer_render_mode(document: MarkdownDocument, profile: ContentProfile) -> RenderMode:
    blocks = document.blocks
    if not blocks:
        return RenderMode.PLAIN_TEXT

    mono_t = (CodeFenceBlock, IndentedCodeBlock, AsciiBlock)
    flow_t = (
        HeadingBlock,
        ParagraphBlock,
        ListBlock,
        BlockquoteBlock,
        TableBlock,
        HrBlock,
    )
    n_mono = sum(1 for b in blocks if isinstance(b, mono_t))
    n_flow = sum(1 for b in blocks if isinstance(b, flow_t))

    if n_mono == 1 and n_flow == 0 and isinstance(blocks[0], CodeFenceBlock):
        return RenderMode.PREFORMATTED
    if n_mono == 1 and n_flow == 0 and isinstance(blocks[0], AsciiBlock):
        return RenderMode.PREFORMATTED
    if n_mono == 1 and n_flow == 0 and isinstance(blocks[0], IndentedCodeBlock):
        return RenderMode.PREFORMATTED

    if n_mono == 0 and n_flow == 1 and isinstance(blocks[0], ParagraphBlock):
        if profile in (ContentProfile.RAW_PLAIN, ContentProfile.ASCII_MONOSPACE):
            return RenderMode.PLAIN_TEXT
        return RenderMode.RICH_TEXT

    if n_mono >= 1 and n_flow >= 1:
        return RenderMode.MIXED_DOCUMENT
    if n_mono >= 1:
        return RenderMode.MIXED_DOCUMENT
    return RenderMode.RICH_TEXT


def block_requires_monospace_font(block: Block) -> bool:
    if isinstance(block, TableBlock):
        return not block.stable
    return isinstance(block, (CodeFenceBlock, IndentedCodeBlock, AsciiBlock))
