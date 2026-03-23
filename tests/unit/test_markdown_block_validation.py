"""Block-Validierung: Tabellen, Code-Fences, ASCII — gleiche Regeln wie Chat/Hilfe."""

from __future__ import annotations

from app.gui.shared.markdown import (
    RenderOptions,
    RenderTarget,
    render_markdown,
    render_segments,
)
from app.gui.shared.markdown.markdown_block_validation import evaluate_table_stability
from app.gui.shared.markdown.markdown_parser import parse_document
from app.gui.shared.markdown.markdown_segment_types import (
    AsciiBlockSegment,
    CodeBlockSegment,
    MalformedBlockSegment,
    PreformattedBlockSegment,
    TableBlockSegment,
)
from app.gui.shared.markdown.markdown_types import CodeFenceBlock, TableBlock


def test_evaluate_table_stable_gfm():
    rows = [["a", "b"], ["1", "2"]]
    raw = ("| a | b |", "|---|---|", "| 1 | 2 |")
    stable, w = evaluate_table_stability(rows, saw_separator=True, raw_lines=raw)
    assert stable is True
    assert w == ()


def test_evaluate_table_unstable_no_separator():
    rows = [["a", "b"], ["1", "2"]]
    raw = ("| a | b |", "| 1 | 2 |")
    stable, w = evaluate_table_stability(rows, saw_separator=False, raw_lines=raw)
    assert stable is False
    assert "missing_separator" in w


def test_evaluate_table_unstable_column_mismatch():
    rows = [["a", "b"], ["only"]]
    raw = ("| a | b |", "|---|---|", "| only |")
    stable, w = evaluate_table_stability(rows, saw_separator=True, raw_lines=raw)
    assert stable is False
    assert "column_mismatch" in w


def test_evaluate_table_unstable_ascii_frame_in_raw():
    rows = [["a", "b"]]
    raw = ("+---+---+", "| a | b |")
    stable, w = evaluate_table_stability(rows, saw_separator=False, raw_lines=raw)
    assert stable is False
    assert "ascii_frame_mix" in w


def test_clean_markdown_table_segment_and_html():
    md = "| Col A | Col B |\n| --- | --- |\n| x | y |\n"
    doc = parse_document(md)
    assert len(doc.blocks) == 1
    tb = doc.blocks[0]
    assert isinstance(tb, TableBlock)
    assert tb.stable is True
    segs = render_segments(md, promote_ascii=False)
    assert len(segs) == 1
    assert isinstance(segs[0], TableBlockSegment)
    r = render_markdown(md, RenderOptions(target=RenderTarget.CHAT_BUBBLE, promote_ascii=False))
    assert "<table" in r.html
    assert "Col A" in r.html and "x" in r.html


def test_defective_table_preformatted_not_html_table():
    md = "| a | b |\n| 1 | 2 |\n| oops |\n"
    doc = parse_document(md)
    tb = doc.blocks[0]
    assert isinstance(tb, TableBlock)
    assert tb.stable is False
    segs = render_segments(md, promote_ascii=False)
    assert isinstance(segs[0], PreformattedBlockSegment)
    assert segs[0].source == "table_fallback"
    r = render_markdown(md, RenderOptions(target=RenderTarget.HELP_BROWSER, promote_ascii=False))
    assert "<table" not in r.html
    assert "<pre" in r.html


def test_ascii_pseudotable_plus_frame_not_proportional_table():
    md = "\n".join(
        [
            "+-------+-------+",
            "|  a    |   b   |",
            "+-------+-------+",
        ]
    )
    segs = render_segments(md)
    kinds = [s.kind for s in segs]
    assert "ascii_block" in kinds or "preformatted_block" in kinds
    assert "table_block" not in kinds
    r = render_markdown(md, RenderOptions(target=RenderTarget.CHAT_BUBBLE))
    assert "<table" not in r.html


def test_fenced_code_complete_segment():
    md = "```python\nprint(1)\n```\n"
    doc = parse_document(md)
    assert isinstance(doc.blocks[0], CodeFenceBlock)
    assert doc.blocks[0].fence_complete is True
    segs = render_segments(md)
    assert isinstance(segs[0], CodeBlockSegment)
    assert segs[0].fence_complete is True


def test_broken_fence_malformed_segment():
    md = "```\nhalf\n"
    segs = render_segments(md)
    assert isinstance(segs[0], MalformedBlockSegment)
    r = render_markdown(md, RenderOptions(target=RenderTarget.CHAT_BUBBLE))
    assert "data-md-malformed" in r.html
    assert "half" in r.html


def test_cli_output_ascii_block():
    md = "ERROR: failed\n  at main (x.py:1)\n  Caused by: boom\n"
    segs = render_segments(md)
    assert any(isinstance(s, AsciiBlockSegment) for s in segs)


def test_mixed_table_code_ascii():
    md = "\n".join(
        [
            "# Report",
            "",
            "| H1 | H2 |",
            "| -- | -- |",
            "| v1 | v2 |",
            "",
            "```",
            "snippet",
            "```",
            "",
            "tree:",
            "└── leaf",
        ]
    )
    segs = render_segments(md)
    kinds = [s.kind for s in segs]
    assert "heading" in kinds
    assert "table_block" in kinds
    assert "code_block" in kinds
    assert "ascii_block" in kinds
    r = render_markdown(md, RenderOptions(target=RenderTarget.GENERIC_HTML))
    assert "<table" in r.html
    assert "<pre" in r.html
