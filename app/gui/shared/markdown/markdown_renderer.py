"""
HTML-Ausgabe für Qt: RenderSegment-Liste (zentrale Darstellungslogik).
"""

from __future__ import annotations

from app.gui.shared.markdown.markdown_inline import parts_to_html
from app.gui.shared.markdown.markdown_segment_builder import blocks_to_render_segments
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
    Block,
    BlockquoteBlock,
    CodeFenceBlock,
    HeadingBlock,
    HrBlock,
    IndentedCodeBlock,
    ListBlock,
    MarkdownDocument,
    ParagraphBlock,
    RenderMode,
    RenderTarget,
    TableBlock,
    AsciiBlock,
)
from app.gui.shared.markdown.markdown_utils import escape_html


def _theme_color_tokens() -> dict[str, str]:
    """Aktive Theme-Tokens (ohne Qt-App: light_default aus Registry)."""
    try:
        from app.gui.themes import get_theme_manager

        mgr = get_theme_manager()
        if mgr.get_theme():
            return mgr.get_tokens()
    except Exception:
        pass
    try:
        from app.gui.themes.registry import ThemeRegistry

        td = ThemeRegistry().get("light_default")
        if td:
            return td.get_tokens_dict()
    except Exception:
        pass
    return {}


def _pre_style(target: RenderTarget) -> str:
    t = _theme_color_tokens()
    bg = (t.get("color_markdown_codeblock_bg") or t.get("color_bg_muted") or "").strip()
    base = (
        "white-space: pre-wrap; font-family: 'DejaVu Sans Mono','Consolas',monospace; "
        "border-radius: 4px; "
    )
    if target == RenderTarget.CHAT_BUBBLE:
        return base + f"font-size: 0.92em; margin: 6px 0; padding: 8px; background-color: {bg};"
    return base + f"font-size: 0.95em; margin: 8px 0; padding: 10px; background-color: {bg};"


def _wrap_root(inner: str, target: RenderTarget) -> str:
    t = _theme_color_tokens()
    body = (t.get("color_markdown_body") or t.get("color_fg_primary") or "").strip()
    color_attr = f"color: {body};" if body else ""
    if target == RenderTarget.CHAT_BUBBLE:
        return f'<div style="font-size: 13px; line-height: 1.45; {color_attr}">{inner}</div>'
    return f'<div style="font-family: sans-serif; line-height: 1.5; {color_attr}">{inner}</div>'


def _code_block_html(seg: CodeBlockSegment, target: RenderTarget) -> str:
    body = escape_html(seg.body)
    lang = escape_html(seg.language) if seg.language else ""
    cls = f' class="{lang}"' if lang else ""
    st = _pre_style(target)
    return f"<pre{cls} style='{st}'><code>{body}</code></pre>"


def _ascii_block_html(seg: AsciiBlockSegment, target: RenderTarget) -> str:
    body = escape_html(seg.body)
    st = _pre_style(target)
    return f"<pre style='{st}'><code>{body}</code></pre>"


def _table_style(target: RenderTarget) -> str:
    t = _theme_color_tokens()
    bg = (
        t.get("color_markdown_codeblock_bg")
        or t.get("color_bg_surface_alt")
        or t.get("color_bg_muted")
        or ""
    ).strip()
    base = (
        "border-collapse: collapse; font-family: 'DejaVu Sans Mono','Consolas',monospace; "
        "font-size: 0.92em; margin: 8px 0; width: auto; max-width: 100%;"
    )
    return f"{base} background-color: {bg};"


def _table_cell_style(target: RenderTarget) -> str:
    t = _theme_color_tokens()
    b = (t.get("color_markdown_table_border") or t.get("color_border_default") or "").strip()
    return (
        f"border: 1px solid {b}; padding: 4px 8px; "
        "vertical-align: top; white-space: pre-wrap;"
    )


def _table_block_html(seg: TableBlockSegment, target: RenderTarget) -> str:
    rows_html: list[str] = []
    for row in seg.rows:
        cells = "".join(
            f"<td style='{_table_cell_style(target)}'>{escape_html(c)}</td>" for c in row
        )
        rows_html.append(f"<tr>{cells}</tr>")
    inner = "".join(rows_html)
    ts = _table_style(target)
    return f"<table style='{ts}'>{inner}</table>"


def _preformatted_block_html(seg: PreformattedBlockSegment, target: RenderTarget) -> str:
    body = escape_html(seg.body)
    st = _pre_style(target)
    hint = "table_fallback" if seg.source == "table_fallback" else "preformatted"
    return (
        f"<pre data-md-pre='{hint}' style='{st}'><code>{body}</code></pre>"
    )


def _malformed_block_html(seg: MalformedBlockSegment, target: RenderTarget) -> str:
    body = escape_html(seg.body)
    st = _pre_style(target)
    t = _theme_color_tokens()
    warn = (t.get("color_state_warning") or t.get("color_border_strong") or "").strip()
    extra = f"border-left: 3px solid {warn};"
    return f"<pre data-md-malformed='incomplete_fence' style='{st} {extra}'><code>{body}</code></pre>"


def _plain_block_inner(body: str, target: RenderTarget) -> str:
    if target == RenderTarget.CHAT_BUBBLE:
        return "<br/>".join(escape_html(ln) for ln in body.split("\n"))
    return escape_html(" ".join(x.strip() for x in body.split() if x.strip()))


def _paragraph_inner(seg: ParagraphSegment, target: RenderTarget) -> str:
    if target == RenderTarget.CHAT_BUBBLE:
        return "<br/>".join(parts_to_html(lp) for lp in seg.lines)
    return " ".join(parts_to_html(lp) for lp in seg.lines)


def _segment_to_html(seg: RenderSegment, target: RenderTarget) -> str:
    if isinstance(seg, HeadingSegment):
        lvl = max(1, min(6, seg.level))
        inner = parts_to_html(seg.parts)
        return f"<h{lvl} style='margin: 10px 0 6px 0;'>{inner}</h{lvl}>"

    if isinstance(seg, ParagraphSegment):
        inner = _paragraph_inner(seg, target)
        if not inner.strip():
            return ""
        return f"<p style='margin: 6px 0;'>{inner}</p>"

    if isinstance(seg, PlainBlockSegment):
        inner = _plain_block_inner(seg.body, target)
        if not inner.strip():
            return ""
        return f"<p style='margin: 6px 0;'>{inner}</p>"

    if isinstance(seg, CodeBlockSegment):
        return _code_block_html(seg, target)

    if isinstance(seg, MalformedBlockSegment):
        return _malformed_block_html(seg, target)

    if isinstance(seg, TableBlockSegment):
        return _table_block_html(seg, target)

    if isinstance(seg, PreformattedBlockSegment):
        return _preformatted_block_html(seg, target)

    if isinstance(seg, AsciiBlockSegment):
        return _ascii_block_html(seg, target)

    if isinstance(seg, BulletListSegment):
        lis = []
        for item in seg.items:
            inner = parts_to_html(item)
            lis.append(f"<li style='margin: 2px 0;'>{inner}</li>")
        return f"<ul style='margin: 6px 0; padding-left: 22px;'>{''.join(lis)}</ul>"

    if isinstance(seg, OrderedListSegment):
        lis = []
        for item in seg.items:
            inner = parts_to_html(item)
            lis.append(f"<li style='margin: 2px 0;'>{inner}</li>")
        return f"<ol style='margin: 6px 0; padding-left: 22px;'>{''.join(lis)}</ol>"

    if isinstance(seg, QuoteSegment):
        parts = []
        for lp in seg.lines:
            inner = parts_to_html(lp)
            parts.append(f"<p style='margin: 4px 0;'>{inner}</p>")
        inner = "".join(parts) or "<p></p>"
        t = _theme_color_tokens()
        qb = (t.get("color_markdown_quote_border") or t.get("color_border_strong") or "").strip()
        return (
            f"<blockquote style='margin: 8px 0; padding-left: 12px; "
            f"border-left: 3px solid {qb};'>{inner}</blockquote>"
        )

    if isinstance(seg, SeparatorSegment):
        t = _theme_color_tokens()
        hr = (t.get("color_markdown_hr") or t.get("color_border_subtle") or "").strip()
        return f"<hr style='border: none; border-top: 1px solid {hr}; margin: 12px 0;'/>"

    if isinstance(seg, InlineCodeSegment):
        return f"<p style='margin: 6px 0;'><code>{escape_html(seg.text)}</code></p>"

    return ""


def render_segments_to_html(
    segments: list[RenderSegment],
    *,
    mode: RenderMode,
    target: RenderTarget,
) -> str:
    if not segments:
        return _wrap_root("", target)

    if mode == RenderMode.PLAIN_TEXT and len(segments) == 1:
        s0 = segments[0]
        if isinstance(s0, PlainBlockSegment):
            inner = _plain_block_inner(s0.body, target)
            return _wrap_root(f"<p style='margin:0;'>{inner}</p>", target)
        if isinstance(s0, ParagraphSegment):
            inner = _paragraph_inner(s0, target)
            return _wrap_root(f"<p style='margin:0;'>{inner}</p>", target)

    if mode == RenderMode.PREFORMATTED and len(segments) == 1:
        s0 = segments[0]
        if isinstance(s0, CodeBlockSegment):
            return _wrap_root(_code_block_html(s0, target), target)
        if isinstance(s0, MalformedBlockSegment):
            return _wrap_root(_malformed_block_html(s0, target), target)
        if isinstance(s0, AsciiBlockSegment):
            return _wrap_root(_ascii_block_html(s0, target), target)
        if isinstance(s0, PreformattedBlockSegment):
            return _wrap_root(_preformatted_block_html(s0, target), target)
        if isinstance(s0, TableBlockSegment):
            return _wrap_root(_table_block_html(s0, target), target)
        if isinstance(s0, PlainBlockSegment):
            st = _pre_style(target)
            body = escape_html(s0.body)
            return _wrap_root(f"<pre style='{st}'><code>{body}</code></pre>", target)

    inner = "".join(_segment_to_html(s, target) for s in segments)
    return _wrap_root(inner, target)


def document_to_plain_text(doc: MarkdownDocument) -> str:
    sections: list[str] = []
    for b in doc.blocks:
        if isinstance(b, HeadingBlock):
            sections.append(f"{'#' * b.level} {b.text}")
        elif isinstance(b, ParagraphBlock):
            sections.append("\n".join(b.lines))
        elif isinstance(b, CodeFenceBlock):
            lang = b.language or ""
            if b.fence_complete:
                sections.append(f"```{lang}\n{b.body}\n```")
            else:
                sections.append(f"```{lang}\n{b.body}\n")
        elif isinstance(b, IndentedCodeBlock):
            sections.append("\n".join("    " + ln for ln in b.body.split("\n")))
        elif isinstance(b, AsciiBlock):
            sections.append(b.body)
        elif isinstance(b, ListBlock):
            lines = []
            for i, item in enumerate(b.items, start=1):
                prefix = f"{i}. " if b.ordered else "- "
                lines.append(prefix + item)
            sections.append("\n".join(lines))
        elif isinstance(b, BlockquoteBlock):
            sections.append("\n".join("> " + ln for ln in b.lines))
        elif isinstance(b, HrBlock):
            sections.append("---")
        elif isinstance(b, TableBlock):
            if not b.stable and b.raw_lines:
                sections.append("\n".join(b.raw_lines))
            else:
                sections.append("\n".join(" | ".join(row) for row in b.rows))
    return "\n\n".join(s for s in sections if s).strip()


def render_document_html(
    document: MarkdownDocument,
    *,
    mode: RenderMode,
    target: RenderTarget,
) -> str:
    segments = blocks_to_render_segments(document.blocks)
    return render_segments_to_html(segments, mode=mode, target=target)


def blocks_to_segments(blocks: list[Block]) -> list[RenderSegment]:
    """Öffentliche Hilfs-API: nur Konvertierung Block → Segment."""
    return blocks_to_render_segments(blocks)
