"""Unit tests: zentrale Markdown-Pipeline (ohne Qt-Fixtures)."""

from app.gui.shared.markdown import (
    RenderMode,
    RenderOptions,
    RenderTarget,
    markdown_to_html,
    render_markdown,
)
from app.gui.shared.markdown.markdown_parser import parse_document
from app.gui.shared.markdown.markdown_types import CodeFenceBlock, ListBlock, ParagraphBlock


def test_plain_short_chat_is_plain_mode():
    r = render_markdown("hello", RenderOptions(target=RenderTarget.CHAT_BUBBLE))
    assert r.mode == RenderMode.PLAIN_TEXT
    assert "hello" in r.html
    assert r.plain_text == "hello"


def test_heading_list_fence_parse():
    md = "# T\n\n- a\n- b\n\n```\nx\n```"
    doc = parse_document(md)
    kinds = [type(b).__name__ for b in doc.blocks]
    assert "HeadingBlock" in kinds
    assert "ListBlock" in kinds
    assert "CodeFenceBlock" in kinds


def test_fence_preserves_spaces():
    md = "```\n  tree\n  |-- a\n```"
    r = render_markdown(md, RenderOptions(target=RenderTarget.HELP_BROWSER))
    assert "  tree" in r.html
    assert "<pre" in r.html
    assert r.document.blocks
    assert isinstance(r.document.blocks[0], CodeFenceBlock)


def test_ascii_paragraph_promoted_to_monospace_block():
    # Keine Markdown-Tabelle (|…|), sonst TableBlock statt ein Absatz
    md = "\n".join(
        [
            "project/",
            "├── src/",
            "│   └── main.py",
            "└── README.md",
        ]
    )
    r = render_markdown(md, RenderOptions(target=RenderTarget.GENERIC_HTML))
    assert any(type(b).__name__ == "AsciiBlock" for b in r.document.blocks)


def test_markdown_to_html_help_wrapper():
    html = markdown_to_html("## Hi\n\n**x**")
    assert "<h2" in html
    assert "<b>" in html or "Hi" in html


def test_chat_preserves_line_breaks_in_paragraph():
    md = "line1\nline2\nline3"
    r = render_markdown(md, RenderOptions(target=RenderTarget.CHAT_BUBBLE))
    assert "<br/>" in r.html
    assert "line1" in r.html and "line3" in r.html


def test_ordered_list_block():
    doc = parse_document("1. first\n2. second")
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], ListBlock)
    assert doc.blocks[0].ordered is True
    assert len(doc.blocks[0].items) == 2
