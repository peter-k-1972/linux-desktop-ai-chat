#!/usr/bin/env python3
"""
Export docs_manual/**/*.md to LaTeX under docs_manual_latex/.

- ASCII-first .tex output (umlauts as TeX escapes; box-drawing in verbatim as + - |).
- Headings: # -> \\section, ## -> \\subsection, ### -> \\subsubsection
- Lists: itemize / enumerate
- Fenced code: verbatim

Run from repo root:
    python tools/manual_to_latex.py
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANUAL_ROOT = PROJECT_ROOT / "docs_manual"
LATEX_ROOT = PROJECT_ROOT / "docs_manual_latex"

INTRO_FILES = ["README.md", "architecture.md", "standards.md"]

# Unicode outside ASCII -> TeX or ASCII (sources stay readable; output is ASCII).
_CHAR_MAP: dict[str, str] = {
    "\u00a0": " ",
    "\u2013": "--",
    "\u2014": "---",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": "``",
    "\u201d": "''",
    "\u2026": r"\ldots{}",
    "\u00e4": r'\"a',
    "\u00f6": r'\"o',
    "\u00fc": r'\"u',
    "\u00df": r"\ss{}",
    "\u00c4": r'\"A',
    "\u00d6": r'\"O',
    "\u00dc": r'\"U',
    "\u2192": r"$\rightarrow$",
    "\u2190": r"$\leftarrow$",
    "\u25bc": "v",
    "\u25b2": "^",
    "\u2022": r"\textbullet{}",
}

_BOX_TO_ASCII = str.maketrans(
    {
        "\u250c": "+",
        "\u2510": "+",
        "\u2514": "+",
        "\u2518": "+",
        "\u2500": "-",
        "\u2502": "|",
        "\u251c": "+",
        "\u2524": "+",
        "\u252c": "+",
        "\u2534": "+",
        "\u253c": "+",
    }
)


def _to_ascii_tex(s: str, *, for_tt: bool = False) -> str:
    out: list[str] = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch)
        elif ch == "\u2026" and for_tt:
            out.append("...")
        else:
            out.append(_CHAR_MAP.get(ch, "?"))
    return "".join(out)


def _asciify_verbatim_line(line: str) -> str:
    return _to_ascii_tex(line).translate(_BOX_TO_ASCII)


def _escape_latex_plain(s: str) -> str:
    s = _to_ascii_tex(s)
    repl = (
        ("\\", r"\textbackslash{}"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("$", r"\$"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("^", r"\textasciicircum{}"),
        ("~", r"\textasciitilde{}"),
    )
    for a, b in repl:
        s = s.replace(a, b)
    return s


def _escape_tt(s: str) -> str:
    s = _to_ascii_tex(s, for_tt=True)
    for a, b in (
        ("\\", r"\textbackslash{}"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("_", r"\_"),
        ("$", r"\$"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("^", r"\textasciicircum{}"),
        ("~", r"\textasciitilde{}"),
    ):
        s = s.replace(a, b)
    return s


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_ORDERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def _apply_inline_markup(text: str) -> str:
    """Escape plain text regions; preserve `` `...` ``, **bold**, *italic*, links."""
    text = _to_ascii_tex(text)
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j != -1:
                inner = text[i + 1 : j]
                parts.append(r"\texttt{" + _escape_tt(inner) + "}")
                i = j + 1
                continue
        if i + 1 < n and text[i : i + 2] == "**":
            j = text.find("**", i + 2)
            if j != -1:
                inner = text[i + 2 : j]
                parts.append(r"\textbf{" + _escape_latex_plain(inner) + "}")
                i = j + 2
                continue
        if text[i] == "*" and (i + 1 >= n or text[i + 1] != "*"):
            j = text.find("*", i + 1)
            if j != -1:
                inner = text[i + 1 : j]
                parts.append(r"\textit{" + _escape_latex_plain(inner) + "}")
                i = j + 1
                continue
        m = _LINK_RE.search(text, i)
        if m and m.start() == i:
            label, url = m.group(1), m.group(2)
            parts.append(_escape_latex_plain(label) + r" (\texttt{" + _escape_tt(url) + "})")
            i = m.end()
            continue
        parts.append(_escape_latex_plain(text[i]))
        i += 1
    return "".join(parts)


def _heading_command(level: int, title_plain: str) -> str:
    title = _apply_inline_markup(title_plain.strip())
    if level <= 1:
        return r"\section{" + title + "}"
    if level == 2:
        return r"\subsection{" + title + "}"
    if level == 3:
        return r"\subsubsection{" + title + "}"
    if level == 4:
        return r"\paragraph{" + title + "}"
    return r"\subparagraph{" + title + "}"


def _is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _is_table_sep(line: str) -> bool:
    s = line.strip()
    if not _is_table_row(line):
        return False
    inner = s.strip("|")
    return bool(re.fullmatch(r"[\s|\-:]+", inner))


def _split_table_cells(row: str) -> list[str]:
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _table_to_latex(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    cols = max(len(r) for r in rows)
    spec = "l" * cols
    out = [r"\begin{center}", r"\begin{tabular}{" + spec + "}", r"\hline"]
    for i, row in enumerate(rows):
        cells = [_apply_inline_markup(c) for c in row]
        while len(cells) < cols:
            cells.append("")
        out.append(" & ".join(cells) + r" \\")
        if i == 0:
            out.append(r"\hline")
    out.append(r"\hline")
    out.append(r"\end{tabular}")
    out.append(r"\end{center}")
    return out


def markdown_to_latex(md: str) -> str:
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_code = False
    code_buf: list[str] = []

    def flush_code() -> None:
        nonlocal code_buf
        out.append(r"\begin{verbatim}")
        for cl in code_buf:
            out.append(_asciify_verbatim_line(cl.rstrip("\n")))
        out.append(r"\end{verbatim}")
        code_buf = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if in_code:
            if stripped.startswith("```"):
                flush_code()
                in_code = False
                i += 1
                continue
            code_buf.append(raw.rstrip("\n"))
            i += 1
            continue

        if stripped.startswith("```"):
            in_code = True
            code_buf = []
            lang = stripped[3:].strip()
            if lang and re.fullmatch(r"[A-Za-z0-9_.+-]+", lang):
                i += 1
            else:
                if lang:
                    code_buf.append(lang)
                i += 1
            continue

        if _is_table_row(raw):
            table_rows: list[list[str]] = []
            while i < len(lines) and _is_table_row(lines[i]):
                row_line = lines[i].strip()
                if _is_table_sep(row_line):
                    i += 1
                    continue
                table_rows.append(_split_table_cells(row_line))
                i += 1
            out.extend(_table_to_latex(table_rows))
            out.append("")
            continue

        m = _HEADING_RE.match(raw)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            out.append(_heading_command(level, title))
            out.append("")
            i += 1
            continue

        if stripped == "":
            out.append("")
            i += 1
            continue

        if stripped == "---" or stripped == "***":
            out.append(r"\hline")
            out.append("")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q = lines[i].strip().lstrip(">").strip()
                quote_lines.append(_apply_inline_markup(q))
                i += 1
            out.append(r"\begin{quote}")
            out.append(" ".join(quote_lines))
            out.append(r"\end{quote}")
            out.append("")
            continue

        om = _ORDERED_RE.match(stripped)
        um = stripped.startswith("- ") or stripped.startswith("* ")
        if om or um:
            use_enum = bool(om)
            out.append(r"\begin{enumerate}" if use_enum else r"\begin{itemize}")
            while i < len(lines):
                s = lines[i].strip()
                om2 = _ORDERED_RE.match(s)
                um2 = s.startswith("- ") or s.startswith("* ")
                if not om2 and not um2:
                    break
                if use_enum and um2:
                    break
                if not use_enum and om2:
                    break
                if om2:
                    body = om2.group(2)
                else:
                    body = s[2:].strip()
                out.append(r"\item " + _apply_inline_markup(body))
                i += 1
            out.append(r"\end{enumerate}" if use_enum else r"\end{itemize}")
            out.append("")
            continue

        out.append(_apply_inline_markup(raw.rstrip()))
        i += 1

    if in_code:
        flush_code()

    tex = "\n".join(out)
    tex = re.sub(r"\n{3,}", "\n\n", tex).strip() + "\n"
    return tex


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="ascii", errors="strict")


def _build_intro() -> str:
    chunks: list[str] = []
    for name in INTRO_FILES:
        p = MANUAL_ROOT / name
        if p.is_file():
            chunks.append(p.read_text(encoding="utf-8"))
    return markdown_to_latex("\n\n".join(chunks))


def _collect_modules() -> list[str]:
    base = MANUAL_ROOT / "modules"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir() if d.is_dir() and (d / "README.md").is_file())


def _collect_workflows() -> list[str]:
    base = MANUAL_ROOT / "workflows"
    if not base.is_dir():
        return []
    return sorted(p.stem for p in base.glob("*.md"))


def _collect_roles() -> list[str]:
    base = MANUAL_ROOT / "roles"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir() if d.is_dir() and (d / "README.md").is_file())


def _generate_structure_tex(module_names: list[str], workflow_stems: list[str], role_names: list[str]) -> str:
    lines = [
        "% AUTO-GENERATED by tools/manual_to_latex.py -- do not edit by hand.",
        r"\chapter{Einleitung}",
        r"\input{intro}",
        "",
        r"\chapter{Module}",
    ]
    for m in module_names:
        lines.append(rf"\input{{modules/{m}}}")
    lines.append("")
    lines.append(r"\chapter{Workflows}")
    for w in workflow_stems:
        lines.append(rf"\input{{workflows/{w}}}")
    lines.append("")
    lines.append(r"\chapter{Rollen}")
    for r in role_names:
        lines.append(rf"\input{{roles/{r}}}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not MANUAL_ROOT.is_dir():
        raise SystemExit(f"Missing manual root: {MANUAL_ROOT}")

    LATEX_ROOT.mkdir(parents=True, exist_ok=True)
    (LATEX_ROOT / "modules").mkdir(exist_ok=True)
    (LATEX_ROOT / "workflows").mkdir(exist_ok=True)
    (LATEX_ROOT / "roles").mkdir(exist_ok=True)

    _write(LATEX_ROOT / "intro.tex", _build_intro())

    module_names = _collect_modules()
    for name in module_names:
        src = MANUAL_ROOT / "modules" / name / "README.md"
        _write(LATEX_ROOT / "modules" / f"{name}.tex", markdown_to_latex(src.read_text(encoding="utf-8")))

    workflow_stems = _collect_workflows()
    for stem in workflow_stems:
        src = MANUAL_ROOT / "workflows" / f"{stem}.md"
        _write(LATEX_ROOT / "workflows" / f"{stem}.tex", markdown_to_latex(src.read_text(encoding="utf-8")))

    role_names = _collect_roles()
    for name in role_names:
        src = MANUAL_ROOT / "roles" / name / "README.md"
        _write(LATEX_ROOT / "roles" / f"{name}.tex", markdown_to_latex(src.read_text(encoding="utf-8")))

    structure = _generate_structure_tex(module_names, workflow_stems, role_names)
    _write(LATEX_ROOT / "structure.tex", structure)

    print(f"Wrote LaTeX export under {LATEX_ROOT}")
    print(f"  intro + {len(module_names)} modules + {len(workflow_stems)} workflows + {len(role_names)} roles")


if __name__ == "__main__":
    main()
