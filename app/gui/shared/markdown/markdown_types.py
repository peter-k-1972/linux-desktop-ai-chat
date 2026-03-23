"""
Structured types for the GUI Markdown pipeline (parse → normalize → render).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeAlias, Union


class BlockKind(Enum):
    HEADING = auto()
    PARAGRAPH = auto()
    CODE_FENCE = auto()
    INDENTED_CODE = auto()
    ASCII_BLOCK = auto()  # monospace-pflichtig, aus Heuristik
    BULLET_LIST = auto()
    ORDERED_LIST = auto()
    BLOCKQUOTE = auto()
    HR = auto()
    TABLE = auto()


class ContentProfile(Enum):
    """Erkannte Quelle / dominanter Inhaltstyp (vor Render-Modus)."""

    MARKDOWN_FLOW = auto()
    RAW_PLAIN = auto()
    FENCED_CODE_ONLY = auto()
    ASCII_MONOSPACE = auto()


class RenderMode(Enum):
    """Ausgabe-Modus der Pipeline (nach Klassifikation + Block-Mix)."""

    RICH_TEXT = auto()
    PLAIN_TEXT = auto()
    PREFORMATTED = auto()
    MIXED_DOCUMENT = auto()


class RenderTarget(Enum):
    """Ziel-Kontext beeinflusst u. a. Pre/Code-Whitespace (Chat vs. Hilfe)."""

    HELP_BROWSER = auto()
    CHAT_BUBBLE = auto()
    GENERIC_HTML = auto()


@dataclass
class HeadingBlock:
    level: int
    text: str  # Rohzeile ohne #


@dataclass
class ParagraphBlock:
    lines: list[str]


@dataclass
class CodeFenceBlock:
    language: str
    body: str  # inkl. Zeilenumbrüche, ohne Fence-Zeilen
    fence_complete: bool = True  # False: schließende ``` fehlt (toleranter Preformatted-Fallback)


@dataclass
class IndentedCodeBlock:
    body: str


@dataclass
class AsciiBlock:
    """Monospace-Pflichtblock (Diagramm, CLI, Pseudotabelle)."""

    body: str


@dataclass
class ListBlock:
    ordered: bool
    items: list[str]  # je Eintrag ein Fließtext (ohne Marker)


@dataclass
class BlockquoteBlock:
    lines: list[str]


@dataclass
class HrBlock:
    pass


@dataclass
class TableBlock:
    rows: list[list[str]]  # Zellen roh, getrimmt
    stable: bool = True
    structural_warnings: tuple[str, ...] = ()
    raw_lines: tuple[str, ...] = ()  # Original-|-Zeilen für Preformatted-Fallback


Block = Union[
    HeadingBlock,
    ParagraphBlock,
    CodeFenceBlock,
    IndentedCodeBlock,
    AsciiBlock,
    ListBlock,
    BlockquoteBlock,
    HrBlock,
    TableBlock,
]


@dataclass
class MarkdownDocument:
    blocks: list[Block] = field(default_factory=list)
    source_normalized: str = ""


@dataclass
class RenderResult:
    """Ergebnis der Rendering-Pipeline."""

    mode: RenderMode
    profile: ContentProfile
    html: str
    plain_text: str
    document: MarkdownDocument


ParsedMarkdownDocument: TypeAlias = MarkdownDocument

