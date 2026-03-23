"""
Öffentliche Parser-/Segment-API (ohne Qt).

parse_markdown / normalize_markdown / render_segments
"""

from __future__ import annotations

from app.gui.shared.markdown.markdown_normalizer import normalize_markdown
from app.gui.shared.markdown.markdown_parser import parse_document
from app.gui.shared.markdown.markdown_segment_builder import blocks_to_render_segments
from app.gui.shared.markdown.markdown_segment_types import RenderSegment
from app.gui.shared.markdown.markdown_types import ParsedMarkdownDocument


def parse_markdown(
    text: str, *, promote_ascii: bool = True
) -> ParsedMarkdownDocument:
    """
    Normalisiert (im Parser), parst und optional ASCII-Promotion.
    Rückgabe: Block-AST + normalisierter Quelltext.
    """
    from app.gui.shared.markdown.markdown_normalizer import promote_ascii_paragraphs

    doc = parse_document(text or "")
    if promote_ascii:
        doc = promote_ascii_paragraphs(doc)
    return doc


def render_segments(
    text: str, *, promote_ascii: bool = True
) -> list[RenderSegment]:
    """
    Pipeline bis zu GUI-neutralen RenderSegmenten (kein HTML, keine Widgets).
    """
    doc = parse_markdown(text, promote_ascii=promote_ascii)
    return blocks_to_render_segments(doc.blocks)
