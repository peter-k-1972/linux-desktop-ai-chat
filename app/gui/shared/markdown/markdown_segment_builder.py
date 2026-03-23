"""
Block-AST → GUI-neutrale RenderSegment-Liste (keine QWidget-Abhängigkeit).
"""

from __future__ import annotations

from app.gui.shared.markdown.markdown_inline import (
    line_has_inline_markdown,
    line_to_parts_or_plain,
    parse_inline_parts,
    try_only_inline_code_line,
)
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
    AsciiBlock,
    Block,
    BlockquoteBlock,
    CodeFenceBlock,
    HeadingBlock,
    HrBlock,
    IndentedCodeBlock,
    ListBlock,
    ParagraphBlock,
    TableBlock,
)


def blocks_to_render_segments(blocks: list[Block]) -> list[RenderSegment]:
    out: list[RenderSegment] = []
    for b in blocks:
        seg = _block_to_segment(b)
        if isinstance(seg, list):
            out.extend(seg)
        elif seg is not None:
            out.append(seg)
    return out


def _block_to_segment(b: Block) -> RenderSegment | list[RenderSegment] | None:
    if isinstance(b, HeadingBlock):
        return HeadingSegment(
            level=max(1, min(6, b.level)),
            parts=parse_inline_parts(b.text),
        )

    if isinstance(b, ParagraphBlock):
        return _paragraph_block_to_segment(b)

    if isinstance(b, CodeFenceBlock):
        if not b.fence_complete:
            return MalformedBlockSegment(
                body=b.body,
                language=b.language or "",
            )
        return CodeBlockSegment(
            language=b.language or "",
            body=b.body,
            fenced=True,
            fence_complete=True,
        )

    if isinstance(b, IndentedCodeBlock):
        return CodeBlockSegment(
            language="", body=b.body, fenced=False, fence_complete=True
        )

    if isinstance(b, AsciiBlock):
        return AsciiBlockSegment(body=b.body)

    if isinstance(b, ListBlock):
        items = tuple(parse_inline_parts(item) for item in b.items)
        if b.ordered:
            return OrderedListSegment(items=items)
        return BulletListSegment(items=items)

    if isinstance(b, BlockquoteBlock):
        lines = tuple(line_to_parts_or_plain(ln) for ln in b.lines)
        return QuoteSegment(lines=lines)

    if isinstance(b, HrBlock):
        return SeparatorSegment()

    if isinstance(b, TableBlock):
        if b.stable:
            return TableBlockSegment(
                rows=tuple(tuple(r) for r in b.rows),
            )
        body = "\n".join(b.raw_lines) if b.raw_lines else "\n".join(
            " | ".join(row) for row in b.rows
        )
        return PreformattedBlockSegment(body=body, source="table_fallback")

    return None


def _paragraph_block_to_segment(b: ParagraphBlock) -> RenderSegment:
    lines = b.lines
    if not lines:
        return PlainBlockSegment(body="")

    if len(lines) == 1:
        ic = try_only_inline_code_line(lines[0])
        if ic:
            return InlineCodeSegment(text=ic.text)

    if not any(line_has_inline_markdown(ln) for ln in lines):
        return PlainBlockSegment(body="\n".join(lines))

    line_parts = tuple(line_to_parts_or_plain(ln.rstrip("\n")) for ln in lines)
    return ParagraphSegment(lines=line_parts)
