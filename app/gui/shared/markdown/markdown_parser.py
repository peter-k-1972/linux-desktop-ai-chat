"""
Block-Level-Parsing: deterministisch, tolerant gegen unvollständiges Markdown.
"""

from __future__ import annotations

import re
from typing import Optional

from app.gui.shared.markdown.markdown_block_validation import evaluate_table_stability
from app.gui.shared.markdown.markdown_normalizer import normalize_source
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
    TableBlock,
)

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_HR = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
_UL_ITEM = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_OL_ITEM = re.compile(r"^(\s*)\d+\.\s+(.*)$")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")


def parse_document(text: str) -> MarkdownDocument:
    src = normalize_source(text)
    lines = src.split("\n")
    blocks: list[Block] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.lstrip().startswith("```"):
            blk, j = _parse_fence(lines, i)
            blocks.append(blk)
            i = j
            continue

        ind = _try_indented_code_block(lines, i)
        if ind is not None:
            blk, j = ind
            blocks.append(blk)
            i = j
            continue

        hm = _HEADING.match(line)
        if hm:
            level = len(hm.group(1))
            blocks.append(HeadingBlock(level=level, text=hm.group(2).strip()))
            i += 1
            continue

        if _HR.match(line.strip()):
            blocks.append(HrBlock())
            i += 1
            continue

        tbl = _try_table(lines, i)
        if tbl is not None:
            tblk, j = tbl
            blocks.append(tblk)
            i = j
            continue

        lst = _try_list(lines, i)
        if lst is not None:
            lblk, j = lst
            blocks.append(lblk)
            i = j
            continue

        if line.lstrip().startswith(">"):
            bq, j = _parse_blockquote(lines, i)
            blocks.append(bq)
            i = j
            continue

        para, j = _parse_paragraph(lines, i)
        blocks.append(para)
        i = j

    return MarkdownDocument(blocks=blocks, source_normalized=src)


def _parse_fence(lines: list[str], start: int) -> tuple[CodeFenceBlock, int]:
    first = lines[start]
    rest = first.lstrip()[3:]
    lang = rest.strip()
    body_lines: list[str] = []
    i = start + 1
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            return (
                CodeFenceBlock(
                    language=lang,
                    body="\n".join(body_lines),
                    fence_complete=True,
                ),
                i + 1,
            )
        body_lines.append(ln)
        i += 1
    return (
        CodeFenceBlock(
            language=lang,
            body="\n".join(body_lines),
            fence_complete=False,
        ),
        i,
    )


def _try_indented_code_block(
    lines: list[str], start: int
) -> Optional[tuple[IndentedCodeBlock, int]]:
    ln0 = lines[start]
    if ln0.startswith("    ") and (_UL_ITEM.match(ln0) or _OL_ITEM.match(ln0)):
        return None
    if not ln0.startswith("    ") and not ln0.startswith("\t"):
        return None
    # Kein Tab-Mix: nur 4-Leerzeichen-Convention
    if lines[start].startswith("\t"):
        body: list[str] = []
        i = start
        while i < len(lines) and lines[i].startswith("\t"):
            body.append(lines[i][1:] if lines[i] else "")
            i += 1
        if body:
            return IndentedCodeBlock(body="\n".join(body)), i
        return None

    body_lines: list[str] = []
    i = start
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            break
        if ln.startswith("    "):
            body_lines.append(ln[4:])
            i += 1
        elif ln.startswith("\t"):
            body_lines.append(ln[1:])
            i += 1
        else:
            break
    if not body_lines:
        return None
    return IndentedCodeBlock(body="\n".join(body_lines)), i


def _try_list(lines: list[str], start: int) -> Optional[tuple[ListBlock, int]]:
    line = lines[start]
    ul = _UL_ITEM.match(line)
    ol = _OL_ITEM.match(line)
    if not ul and not ol:
        return None
    ordered = bool(ol)
    items: list[str] = []
    i = start

    def item_pattern():
        return _OL_ITEM if ordered else _UL_ITEM

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            break
        m = item_pattern().match(ln)
        if m:
            items.append(m.group(2).strip())
            i += 1
            continue
        # Fortsetzungszeile (eingerückt, kein neuer Marker)
        if items and (ln.startswith("   ") or ln.startswith("  ")) and not _HEADING.match(
            ln
        ):
            cont = ln.strip()
            if cont:
                items[-1] = f"{items[-1]} {cont}"
            i += 1
            continue
        break

    if not items:
        return None
    return ListBlock(ordered=ordered, items=items), i


def _try_table(lines: list[str], start: int) -> Optional[tuple[TableBlock, int]]:
    if not _TABLE_ROW.match(lines[start]):
        return None
    rows: list[list[str]] = []
    raw_buf: list[str] = []
    saw_separator = False
    i = start
    while i < len(lines) and _TABLE_ROW.match(lines[i]):
        line = lines[i]
        raw_buf.append(line)
        raw = line.strip()
        cells = [c.strip() for c in raw.strip("|").split("|")]
        # Trennzeile |---|---|
        if cells and all(re.match(r"^:?-+:?$", c) for c in cells if c):
            saw_separator = True
            i += 1
            continue
        rows.append(cells)
        i += 1
    if len(rows) < 1:
        return None
    raw_t = tuple(raw_buf)
    stable, warnings = evaluate_table_stability(
        rows, saw_separator=saw_separator, raw_lines=raw_t
    )
    return (
        TableBlock(
            rows=rows,
            stable=stable,
            structural_warnings=warnings,
            raw_lines=raw_t,
        ),
        i,
    )


def _parse_blockquote(lines: list[str], start: int) -> tuple[BlockquoteBlock, int]:
    out: list[str] = []
    i = start
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            break
        s = ln.lstrip()
        if not s.startswith(">"):
            break
        # Entferne führendes > und ein optionales Leerzeichen
        content = s[1:].lstrip() if len(s) > 1 else ""
        out.append(content)
        i += 1
    return BlockquoteBlock(lines=out), i


def _parse_paragraph(lines: list[str], start: int) -> tuple[ParagraphBlock, int]:
    buf: list[str] = []
    i = start
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            break
        if (
            ln.lstrip().startswith("```")
            or _HEADING.match(ln)
            or _HR.match(ln.strip())
            or _UL_ITEM.match(ln)
            or _OL_ITEM.match(ln)
            or _TABLE_ROW.match(ln)
            or ln.lstrip().startswith(">")
        ):
            break
        if ln.startswith("    ") and not buf:
            break
        buf.append(ln)
        i += 1
    return ParagraphBlock(lines=buf), i
