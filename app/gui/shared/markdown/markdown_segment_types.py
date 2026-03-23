"""
GUI-neutrale Render-Segmente (keine Qt-/HTML-Abhängigkeit in der Parser-Schicht).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union


# --- Inline-Teile (in Fließtext-Segmenten) ---


@dataclass(frozen=True)
class TextPart:
    text: str


@dataclass(frozen=True)
class InlineCodePart:
    text: str


@dataclass(frozen=True)
class BoldPart:
    text: str


@dataclass(frozen=True)
class ItalicPart:
    text: str


@dataclass(frozen=True)
class LinkPart:
    label: str
    href: str


ParagraphPart = Union[TextPart, InlineCodePart, BoldPart, ItalicPart, LinkPart]

LineParts = tuple[ParagraphPart, ...]
LinesParts = tuple[LineParts, ...]


# --- Block-Segmente ---


@dataclass(frozen=True)
class HeadingSegment:
    kind: Literal["heading"] = "heading"
    level: int = 1
    parts: LineParts = field(default_factory=tuple)


@dataclass(frozen=True)
class ParagraphSegment:
    """Ein oder mehrere Zeilen; pro Zeile eigene Inline-Parts (Zeilenumbrüche im Ziel-Renderer)."""

    kind: Literal["paragraph"] = "paragraph"
    lines: LinesParts = field(default_factory=tuple)


@dataclass(frozen=True)
class BulletListSegment:
    kind: Literal["bullet_list"] = "bullet_list"
    items: tuple[LineParts, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OrderedListSegment:
    kind: Literal["ordered_list"] = "ordered_list"
    items: tuple[LineParts, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CodeBlockSegment:
    kind: Literal["code_block"] = "code_block"
    language: str = ""
    body: str = ""
    fenced: bool = True
    fence_complete: bool = True


@dataclass(frozen=True)
class InlineCodeSegment:
    """Degenerierter Block: eine Zeile nur `inline code` (optional)."""

    kind: Literal["inline_code"] = "inline_code"
    text: str = ""


@dataclass(frozen=True)
class QuoteSegment:
    kind: Literal["quote"] = "quote"
    lines: LinesParts = field(default_factory=tuple)


@dataclass(frozen=True)
class SeparatorSegment:
    kind: Literal["separator"] = "separator"


@dataclass(frozen=True)
class AsciiBlockSegment:
    kind: Literal["ascii_block"] = "ascii_block"
    body: str = ""


@dataclass(frozen=True)
class TableBlockSegment:
    """Stabile GFM-Tabelle — proportional/tabellarisch, Monospace in Zellen für Ausrichtung."""

    kind: Literal["table_block"] = "table_block"
    rows: tuple[tuple[str, ...], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PreformattedBlockSegment:
    """Sicherer Monospace-Fallback (instabile Tabelle, o. Ä.) — niemals proportional umbrechen."""

    kind: Literal["preformatted_block"] = "preformatted_block"
    body: str = ""
    source: Literal["table_fallback", "generic"] = "generic"


@dataclass(frozen=True)
class MalformedBlockSegment:
    """Defekte fenced Codeblöcke (z. B. fehlende schließende Fence) — Preformatted, tolerant."""

    kind: Literal["malformed_block"] = "malformed_block"
    body: str = ""
    language: str = ""


@dataclass(frozen=True)
class PlainBlockSegment:
    """Reiner Text ohne Inline-Markdown-Parsing."""

    kind: Literal["plain_block"] = "plain_block"
    body: str = ""


RenderSegment = Union[
    HeadingSegment,
    ParagraphSegment,
    BulletListSegment,
    OrderedListSegment,
    CodeBlockSegment,
    InlineCodeSegment,
    QuoteSegment,
    SeparatorSegment,
    AsciiBlockSegment,
    PlainBlockSegment,
    TableBlockSegment,
    PreformattedBlockSegment,
    MalformedBlockSegment,
]
