"""Zentrale Parser-/Segment-API: parse_markdown, normalize_markdown, render_segments."""

from __future__ import annotations

from app.gui.shared.markdown import (
    AsciiBlockSegment,
    BulletListSegment,
    CodeBlockSegment,
    HeadingSegment,
    InlineCodeSegment,
    MalformedBlockSegment,
    OrderedListSegment,
    ParagraphSegment,
    PlainBlockSegment,
    QuoteSegment,
    normalize_markdown,
    parse_markdown,
    render_segments,
)
from app.gui.shared.markdown.markdown_segment_types import BoldPart, InlineCodePart, TextPart
from app.gui.shared.markdown.markdown_types import CodeFenceBlock


def _kinds(segs):
    return [s.kind for s in segs]


def test_headings_and_lists_segments():
    md = "## Title\n\n- a\n- b\n\n1. x\n2. y"
    segs = render_segments(md)
    assert "heading" in _kinds(segs)
    assert "bullet_list" in _kinds(segs)
    assert "ordered_list" in _kinds(segs)
    h = next(s for s in segs if s.kind == "heading")
    assert isinstance(h, HeadingSegment)
    assert h.level == 2
    assert any(isinstance(p, TextPart) and "Title" in p.text for p in h.parts)


def test_fenced_code_block_segment():
    md = "```py\nx = 1\n```"
    segs = render_segments(md)
    assert len(segs) == 1
    c = segs[0]
    assert isinstance(c, CodeBlockSegment)
    assert c.fenced is True
    assert c.fence_complete is True
    assert c.language == "py"
    assert "x = 1" in c.body


def test_ascii_tree_structure():
    md = "\n".join(
        [
            "project/",
            "├── src/",
            "│   └── main.py",
            "└── README.md",
        ]
    )
    segs = render_segments(md)
    assert any(s.kind == "ascii_block" for s in segs)
    ab = next(s for s in segs if s.kind == "ascii_block")
    assert isinstance(ab, AsciiBlockSegment)
    assert "├──" in ab.body


def test_pseudotable_becomes_monospace_segment():
    md = "\n".join(
        [
            "+-------+-------+",
            "|  a    |   b   |",
            "+-------+-------+",
        ]
    )
    segs = render_segments(md)
    # +---+ Zeilen → ascii_block; mittlere |-Zeile → instabile Tabelle → preformatted_block
    bodies = "".join(
        s.body for s in segs if s.kind in ("ascii_block", "preformatted_block")
    )
    assert "a" in bodies and "b" in bodies


def test_cli_output_ascii_block():
    md = "\n".join(
        [
            "ERROR: connection refused",
            "  at WorkerThread.run (app.py:42)",
            "  Caused by: Timeout",
        ]
    )
    segs = render_segments(md)
    assert any(s.kind == "ascii_block" for s in segs)


def test_mixed_document_segments():
    md = "\n".join(
        [
            "# Doc",
            "",
            "Intro **bold**.",
            "",
            "```",
            "code here",
            "```",
            "",
            "tree:",
            "└── leaf",
        ]
    )
    segs = render_segments(md)
    kinds = _kinds(segs)
    assert "heading" in kinds
    assert "code_block" in kinds
    assert "ascii_block" in kinds
    assert "paragraph" in kinds or "plain_block" in kinds


def test_broken_markdown_unclosed_fence():
    md = "```\nno closing"
    doc = parse_markdown(md)
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], CodeFenceBlock)
    assert doc.blocks[0].fence_complete is False
    segs = render_segments(md)
    assert len(segs) == 1
    assert isinstance(segs[0], MalformedBlockSegment)
    assert "no closing" in segs[0].body


def test_normalize_mixed_newlines_and_tabs():
    raw = "a\tb\r\nc"
    n = normalize_markdown(raw)
    assert "\r" not in n
    assert n == "a   b\nc" or n.startswith("a") and "b" in n and "c" in n


def test_parse_markdown_returns_normalized_source():
    doc = parse_markdown("x\r\ny")
    assert "\r" not in doc.source_normalized


def test_inline_only_line_is_inline_code_segment():
    segs = render_segments("`pip install x`")
    assert len(segs) == 1
    assert isinstance(segs[0], InlineCodeSegment)
    assert segs[0].text == "pip install x"


def test_quote_and_separator():
    md = "> line\n\n---\n\ntext"
    segs = render_segments(md)
    assert "quote" in _kinds(segs)
    assert "separator" in _kinds(segs)
    q = next(s for s in segs if s.kind == "quote")
    assert isinstance(q, QuoteSegment)


def test_paragraph_with_inline_parts():
    segs = render_segments("Hello **world** and `code`.")
    p = next(s for s in segs if s.kind == "paragraph")
    assert isinstance(p, ParagraphSegment)
    flat = [type(x).__name__ for line in p.lines for x in line]
    assert "BoldPart" in flat
    assert "InlineCodePart" in flat


def test_plain_block_no_markdown():
    segs = render_segments("just\nplain\nlines")
    assert all(s.kind == "plain_block" for s in segs)
    assert isinstance(segs[0], PlainBlockSegment)
