#!/usr/bin/env python3
"""
Index Markdown under README.md, docs/**, help/**, docs_manual/** and split into
heading-based chunks for semantic search / RAG pipelines.

Output: data/doc_index.json

Run: python3 tools/build_doc_index.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "data" / "doc_index.json"

ATX_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*(?:#+\s*)?$")
FRONT_MATTER_START = re.compile(r"^---\s*$")


@dataclass
class DocChunk:
    title: str
    section: str
    content: str
    file_path: str
    anchor: str
    tags: list[str]


def _github_slug(text: str) -> str:
    t = text.strip()
    t = unicodedata.normalize("NFKD", t)
    t = t.lower()
    out: list[str] = []
    for ch in t:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("-")
    s = "".join(out)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "section"


def _strip_inline_heading_id(text: str) -> tuple[str, str | None]:
    """Return (visible_heading, explicit_id) if `{#id}` suffix is present."""
    m = re.search(r"\s*\{#([a-zA-Z0-9_-]+)\}\s*$", text)
    if m:
        return text[: m.start()].strip(), m.group(1)
    return text.strip(), None


def _area_tag(rel: str) -> str:
    if rel == "README.md":
        return "readme"
    if rel.startswith("docs/"):
        return "docs"
    if rel.startswith("help/"):
        return "help"
    if rel.startswith("docs_manual/"):
        return "docs_manual"
    return "other"


def _path_tags(rel: str, area: str) -> list[str]:
    parts = Path(rel).parts
    tags: list[str] = [area]
    for p in parts[:-1]:
        if p and p not in tags:
            tags.append(p)
    stem = Path(rel).stem
    if stem and stem.lower() != "readme" and stem not in tags:
        tags.append(stem)
    return tags[:12]


def _iter_markdown_files(root: Path) -> list[Path]:
    found: list[Path] = []
    readme = root / "README.md"
    if readme.is_file():
        found.append(readme.resolve())
    for name in ("docs", "help", "docs_manual"):
        d = root / name
        if d.is_dir():
            for p in sorted(d.rglob("*.md")):
                if p.is_file():
                    found.append(p.resolve())
    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in found:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def _parse_sections(text: str) -> tuple[str, list[tuple[int, str, int, int]]]:
    """
    Returns (doc_title_hint, sections) where each section is
    (level, heading_text, body_start_line_index, body_end_line_exclusive).
    Line indices are 0-based on splitlines().
    """
    lines = text.splitlines()
    in_fence = False
    i = 0
    if lines and FRONT_MATTER_START.match(lines[0]):
        i = 1
        while i < len(lines) and not FRONT_MATTER_START.match(lines[i]):
            i += 1
        if i < len(lines):
            i += 1

    headings: list[tuple[int, str, int]] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if not in_fence:
            m = ATX_HEADING.match(line)
            if m:
                level = len(m.group(1))
                raw_h = m.group(2).rstrip()
                vis, _explicit = _strip_inline_heading_id(raw_h)
                headings.append((level, vis, i + 1))
        i += 1

    doc_title = ""
    for lev, htext, _ in headings:
        if lev == 1:
            doc_title = htext
            break

    sections: list[tuple[int, str, int, int]] = []
    if not headings:
        return doc_title, sections

    first_h_line = headings[0][2] - 1
    if first_h_line > 0:
        sections.append((0, "", 0, first_h_line))

    for idx, (level, htext, body_start) in enumerate(headings):
        end = len(lines)
        if idx + 1 < len(headings):
            next_line = headings[idx + 1][2] - 1
            if next_line > body_start:
                end = next_line
            else:
                end = body_start
        else:
            end = len(lines)
        sections.append((level, htext, body_start, end))

    return doc_title, sections


def _finalize_anchors(chunks_for_file: list[DocChunk]) -> None:
    counts: dict[str, int] = {}
    for c in chunks_for_file:
        base = c.anchor or "section"
        n = counts.get(base, 0)
        counts[base] = n + 1
        if n > 0:
            c.anchor = f"{base}-{n}"


def index_file(root: Path, path: Path) -> list[DocChunk]:
    rel = str(path.resolve().relative_to(root)).replace("\\", "/")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []

    doc_title, sections = _parse_sections(raw)
    lines = raw.splitlines()
    if doc_title == "":
        doc_title = path.stem.replace("_", " ").replace("-", " ").title() or path.name

    area = _area_tag(rel)
    base_tags = _path_tags(rel, area)

    chunks: list[DocChunk] = []
    stack: list[tuple[int, str]] = []

    for level, heading, start, end in sections:
        body_lines = lines[start:end]
        content = "\n".join(body_lines).strip()

        if level == 0:
            section_label = ""
            anchor = ""
            if not content:
                continue
        else:
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading))
            section_label = " > ".join(h[1] for h in stack)
            vis_heading, explicit_id = _strip_inline_heading_id(heading)
            anchor = explicit_id if explicit_id else _github_slug(vis_heading)

        tags = list(base_tags)
        if level > 0:
            tags.append(f"h{level}")
        tags = list(dict.fromkeys(tags))

        chunks.append(
            DocChunk(
                title=doc_title,
                section=section_label,
                content=content,
                file_path=rel,
                anchor=anchor,
                tags=tags,
            )
        )

    if not sections and lines:
        chunks.append(
            DocChunk(
                title=doc_title,
                section="",
                content="\n".join(lines).strip(),
                file_path=rel,
                anchor="",
                tags=base_tags,
            )
        )

    _finalize_anchors(chunks)
    return chunks


def build_index(root: Path) -> list[dict]:
    all_chunks: list[DocChunk] = []
    for p in _iter_markdown_files(root):
        all_chunks.extend(index_file(root, p))
    return [asdict(c) for c in all_chunks]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build semantic Markdown chunk index.")
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root (default: repository root)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output JSON path (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    out = args.out.resolve()
    chunks = build_index(root)

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "tools/build_doc_index.py",
        "project_root_hint": ".",
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(chunks)} chunks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
