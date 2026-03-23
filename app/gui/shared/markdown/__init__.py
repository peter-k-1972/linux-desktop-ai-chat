"""
Zentrale Markdown-Pipeline für die GUI: Parse → Normalisieren → Modus → HTML/Plain.

Öffentliche API für Chat, Hilfe und weitere QText*-Widgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.gui.shared.markdown.markdown_api import parse_markdown, render_segments
from app.gui.shared.markdown.markdown_normalizer import normalize_markdown, promote_ascii_paragraphs
from app.gui.shared.markdown.markdown_parser import parse_document
from app.gui.shared.markdown.markdown_renderer import (
    document_to_plain_text,
    render_document_html,
)
from app.gui.shared.markdown.markdown_rules import classify_source, infer_render_mode
from app.gui.shared.markdown.markdown_segment_types import (
    AsciiBlockSegment,
    BulletListSegment,
    CodeBlockSegment,
    HeadingSegment,
    InlineCodeSegment,
    MalformedBlockSegment,
    OrderedListSegment,
    ParagraphSegment,
    PlainBlockSegment,
    PreformattedBlockSegment,
    QuoteSegment,
    RenderSegment,
    SeparatorSegment,
    TableBlockSegment,
)
from app.gui.shared.markdown.markdown_types import (
    ContentProfile,
    MarkdownDocument,
    ParsedMarkdownDocument,
    RenderMode,
    RenderResult,
    RenderTarget,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QTextBrowser, QTextEdit


@dataclass(frozen=True)
class RenderOptions:
    """Optionen für einen Render-Durchlauf."""

    target: RenderTarget = RenderTarget.GENERIC_HTML
    promote_ascii: bool = True


def render_markdown(text: str, options: RenderOptions | None = None) -> RenderResult:
    """
    Vollständige Pipeline: normieren (im Parser), parsen, ASCII-Promotion,
    Profil/Modus, HTML + Plaintext-Spiegel.
    """
    opts = options or RenderOptions()
    doc = parse_document(text or "")
    if opts.promote_ascii:
        doc = promote_ascii_paragraphs(doc)
    profile = classify_source(doc.source_normalized)
    mode = infer_render_mode(doc, profile)
    html = render_document_html(doc, mode=mode, target=opts.target)
    plain = document_to_plain_text(doc)
    return RenderResult(
        mode=mode,
        profile=profile,
        html=html,
        plain_text=plain,
        document=doc,
    )


def markdown_to_html(md: str, *, target: RenderTarget = RenderTarget.HELP_BROWSER) -> str:
    """Kurzform: Markdown-String → HTML-Fragment (mit Root-Wrapper)."""
    return render_markdown(md, RenderOptions(target=target)).html


def apply_to_qtext_edit(
    widget: "QTextEdit",
    text: str,
    *,
    options: RenderOptions | None = None,
) -> None:
    """Setzt QTextEdit-Inhalt über die Pipeline (inkl. Fallback)."""
    from app.gui.shared.markdown_ui import apply_markdown_to_widget

    opts = options or RenderOptions(target=RenderTarget.CHAT_BUBBLE)
    apply_markdown_to_widget(
        widget,
        text or "",
        target=opts.target,
        promote_ascii=opts.promote_ascii,
    )


def apply_to_qtext_browser(
    widget: "QTextBrowser",
    text: str,
    *,
    options: RenderOptions | None = None,
) -> None:
    """Setzt QTextBrowser-Inhalt (Hilfe, Inspector mit Rich-Text)."""
    from app.gui.shared.markdown_ui import apply_markdown_to_widget

    opts = options or RenderOptions(target=RenderTarget.HELP_BROWSER)
    apply_markdown_to_widget(
        widget,
        text or "",
        target=opts.target,
        promote_ascii=opts.promote_ascii,
    )


__all__ = [
    "AsciiBlockSegment",
    "BulletListSegment",
    "CodeBlockSegment",
    "ContentProfile",
    "HeadingSegment",
    "InlineCodeSegment",
    "MalformedBlockSegment",
    "MarkdownDocument",
    "OrderedListSegment",
    "ParagraphSegment",
    "ParsedMarkdownDocument",
    "PlainBlockSegment",
    "PreformattedBlockSegment",
    "QuoteSegment",
    "RenderMode",
    "RenderOptions",
    "RenderResult",
    "RenderSegment",
    "RenderTarget",
    "SeparatorSegment",
    "TableBlockSegment",
    "apply_to_qtext_browser",
    "apply_to_qtext_edit",
    "markdown_to_html",
    "normalize_markdown",
    "parse_markdown",
    "promote_ascii_paragraphs",
    "render_markdown",
    "render_segments",
    "parse_document",
]
