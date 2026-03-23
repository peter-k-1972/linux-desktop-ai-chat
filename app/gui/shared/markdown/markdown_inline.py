"""
Inline-Markdown → strukturierte Parts bzw. HTML (ohne Block-Logik).
"""

from __future__ import annotations

import re
from typing import Sequence

from app.gui.shared.markdown.markdown_segment_types import (
    BoldPart,
    InlineCodePart,
    ItalicPart,
    LinkPart,
    LineParts,
    ParagraphPart,
    TextPart,
)
from app.gui.shared.markdown.markdown_utils import escape_html

_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_BOLD_STAR = re.compile(r"\*\*([^*]+)\*\*")
_BOLD_UNDER = re.compile(r"__([^_]+)__")
_ITALIC_STAR = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_ITALIC_UNDER = re.compile(r"(?<!_)_([^_]+)_(?!_)")

# Zeile nur aus einem Inline-Code
_ONLY_INLINE_CODE = re.compile(r"^`([^`]+)`\s*$")

# Heuristik: enthält erkennbares Inline-/Kopf-Markdown
_HAS_INLINE_MARKDOWN = re.compile(
    r"[`]|__|\*\*|\[[^\]]+\]\([^)]+\)|(?<!\*)\*[^*]+\*(?!\*)|(?<!_)_[^_]+_(?!_)"
)


def line_has_inline_markdown(line: str) -> bool:
    return bool(_HAS_INLINE_MARKDOWN.search(line))


def parse_inline_parts(line: str) -> tuple[ParagraphPart, ...]:
    """Eine Zeile in Text / `code` / **bold** / *italic* / links zerlegen."""
    if not line:
        return ()
    out: list[ParagraphPart] = []
    i = 0
    while i < len(line):
        tick = line.find("`", i)
        if tick == -1:
            out.extend(_parse_non_code_parts(line[i:]))
            break
        out.extend(_parse_non_code_parts(line[i:tick]))
        j = line.find("`", tick + 1)
        if j == -1:
            out.append(TextPart(text=line[tick:]))
            break
        out.append(InlineCodePart(text=line[tick + 1 : j]))
        i = j + 1
    return tuple(_merge_adjacent_text(out))


def _parse_non_code_parts(seg: str) -> list[ParagraphPart]:
    if not seg:
        return []
    parts: list[ParagraphPart] = []
    pos = 0
    n = len(seg)
    while pos < n:
        candidates = []
        for name, rx in (
            ("link", _LINK),
            ("bold_s", _BOLD_STAR),
            ("bold_u", _BOLD_UNDER),
            ("italic_s", _ITALIC_STAR),
            ("italic_u", _ITALIC_UNDER),
        ):
            m = rx.search(seg, pos)
            if m:
                candidates.append((m.start(), name, m))
        if not candidates:
            if pos < n:
                parts.append(TextPart(text=seg[pos:]))
            break
        candidates.sort(key=lambda x: x[0])
        start, name, m = candidates[0]
        if start > pos:
            parts.append(TextPart(text=seg[pos:start]))
        if name == "link":
            parts.append(LinkPart(label=m.group(1), href=m.group(2)))
        elif name in ("bold_s", "bold_u"):
            parts.append(BoldPart(text=m.group(1)))
        else:
            parts.append(ItalicPart(text=m.group(1)))
        pos = m.end()
    return parts


def _merge_adjacent_text(parts: list[ParagraphPart]) -> list[ParagraphPart]:
    if not parts:
        return []
    merged: list[ParagraphPart] = []
    for p in parts:
        if merged and isinstance(p, TextPart) and isinstance(merged[-1], TextPart):
            merged[-1] = TextPart(text=merged[-1].text + p.text)
        else:
            merged.append(p)
    return merged


def parts_to_html(parts: Sequence[ParagraphPart]) -> str:
    """Qt-HTML-Subset aus Parts."""
    chunks: list[str] = []
    for p in parts:
        if isinstance(p, TextPart):
            chunks.append(escape_html(p.text))
        elif isinstance(p, InlineCodePart):
            chunks.append(f"<code>{escape_html(p.text)}</code>")
        elif isinstance(p, BoldPart):
            chunks.append(f"<b>{escape_html(p.text)}</b>")
        elif isinstance(p, ItalicPart):
            chunks.append(f"<i>{escape_html(p.text)}</i>")
        elif isinstance(p, LinkPart):
            chunks.append(
                f'<a href="{escape_html(p.href)}">{escape_html(p.label)}</a>'
            )
    return "".join(chunks)


def line_to_parts_or_plain(line: str) -> LineParts:
    if line_has_inline_markdown(line):
        return parse_inline_parts(line)
    return (TextPart(text=line),)


def try_only_inline_code_line(line: str) -> InlineCodePart | None:
    m = _ONLY_INLINE_CODE.match(line.rstrip())
    if m:
        return InlineCodePart(text=m.group(1))
    return None


def render_inline_markdown_to_html(line: str) -> str:
    """Kompatibilität: eine Zeile Inline-Markdown → HTML."""
    return parts_to_html(parse_inline_parts(line))
