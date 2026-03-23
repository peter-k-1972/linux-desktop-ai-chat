#!/usr/bin/env python3
"""
Projektweiter Markdown-Validator mit Fokus auf Renderbarkeit (Chat/Hilfe/Doku).

Deterministisch, rein lokal (keine Netzwerk-Calls).

Usage:
  python3 tools/validate_markdown_docs.py [--output PATH] [--quiet]

Default report: docs/MARKDOWN_VALIDATION_REPORT.md
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = PROJECT_ROOT / "docs" / "MARKDOWN_VALIDATION_REPORT.md"

# --- Heuristiken (an GUI-Pipeline angelehnt; dupliziert, um ohne app-Paket lauffähig zu sein) ---

_CLI_LINE = re.compile(
    r"^\s*(\$\s|#\s|>\s|C:\\|INFO|WARN|ERROR|ERR!|Traceback|at\s+\w|^\[\w+\]|docker\s|kubectl\s|npm\s|pip\s)",
    re.IGNORECASE,
)
_TREE_OR_TABLE = re.compile(r"^[\s│├└┌┐┘┬┴┼─]+\S")
_BOX_LINE = re.compile(r"^[\s\-+|.:=#oO/\\]{6,}$")
_STRUCTURE_CHARS = frozenset("|+-/\\_=<>[]()")

_FENCE_OPEN = re.compile(r"^(?P<indent>\s*)(?P<fence>(`{3,}|~{3,}))(?P<info>.*)$")
_HEADING_LINE = re.compile(r"^(#{1,6})(\s*)(.*)$")
_UL = re.compile(r"^(\s*)[-*+]\s+")
_OL = re.compile(r"^(\s*)\d+\.\s+")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_CELL = re.compile(r"^:?-+:?$")
_MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


@dataclass
class Issue:
    severity: str  # blocker | high | medium | low
    category: str
    line: int
    col: int | None
    message: str
    fix: str
    auto_fixable: bool = False


def _severity_rank(s: str) -> int:
    return {"blocker": 0, "high": 1, "medium": 2, "low": 3}.get(s, 9)


@dataclass
class FileResult:
    path: Path
    rel: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(i.severity == "blocker" for i in self.issues):
            return "blocker"
        if any(i.severity == "high" for i in self.issues):
            return "high"
        if any(i.severity == "medium" for i in self.issues):
            return "medium"
        if self.issues:
            return "low"
        return "ok"


def _collect_markdown_files(root: Path) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    readme = root / "README.md"
    if readme.is_file():
        rp = readme.resolve()
        seen.add(rp)
        out.append(readme)
    for name in ("docs", "help", "docs_manual"):
        d = root / name
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            rp = p.resolve()
            if rp in seen:
                continue
            # skip buried vendor-like paths
            parts = {x.lower() for x in p.relative_to(root).parts}
            if "node_modules" in parts or ".git" in parts:
                continue
            seen.add(rp)
            out.append(p)
    for p in sorted(root.glob("*.md")):
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        out.append(p)
    out.sort(key=lambda x: str(x.resolve()).lower())
    return out


def _slug_anchor(heading_text: str) -> str:
    """GFM-ähnlicher Slug für #fragment-Prüfung."""
    t = heading_text.strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", "-", t.strip())
    t = re.sub(r"-+", "-", t)
    return t.strip("-")


def _line_structure_density(s: str) -> float:
    if not s:
        return 0.0
    hits = sum(1 for c in s if c in _STRUCTURE_CHARS or c in "│├└┌┐┘─")
    return hits / len(s)


def _dominant_ascii_file(lines: list[str]) -> bool:
    """
    Gesamte Datei wirkt wie Tree/CLI-Dump — dann keine „ASCII ohne Fence“-Warnung pro Abschnitt
    (sonst False Positives z. B. bei app-tree.md).
    """
    ne = [ln for ln in lines if ln.strip()]
    if len(ne) < 12:
        return False
    hits = sum(1 for ln in ne if _looks_like_ascii_risk_line(ln))
    return hits / len(ne) >= 0.42


def _looks_like_ascii_risk_line(s: str) -> bool:
    s = s.rstrip()
    if not s or len(s) < 4:
        return False
    # GFM-Tabellen nicht als ASCII/Monospace-Risiko (hohe |/-Dichte ohne Diagramm).
    if _TABLE_ROW.match(s):
        return False
    if _CLI_LINE.match(s):
        return True
    if _TREE_OR_TABLE.match(s):
        return True
    if _BOX_LINE.match(s):
        return True
    boxish = sum(1 for c in s if c in "+-|") / max(len(s), 1)
    if boxish >= 0.18 and len(s) >= 6:
        return True
    if _line_structure_density(s) >= 0.12 and len(s) >= 10:
        return True
    return False


def _count_table_cells(line: str) -> int:
    raw = line.strip()
    return len([c for c in raw.strip("|").split("|") if c.strip() != "" or True])


def _table_cell_parts(line: str) -> list[str]:
    raw = line.strip()
    return [c.strip() for c in raw.strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(_TABLE_SEP_CELL.match(c) for c in cells if c)


def _check_fences_and_tildas(lines: list[str], issues: list[Issue]) -> None:
    """Backtick-Fences (GUI) vs. Tilden; ungeschlossene Blöcke."""
    in_backtick_fence = False
    backtick_open_line = 0
    open_info = ""

    for i, line in enumerate(lines, start=1):
        m = _FENCE_OPEN.match(line)
        if not m:
            continue
        fence = m.group("fence")
        ch = fence[0]
        if ch == "~":
            issues.append(
                Issue(
                    severity="high",
                    category="codeblocks",
                    line=i,
                    col=1,
                    message=(
                        "Tilden-Fence (~~~) wird vom GUI-Parser nicht als Codeblock erkannt; "
                        "Inhalt läuft als Fließtext/Absatz."
                    ),
                    fix="Fence durch ``` (Backticks) ersetzen oder Inhalt anders strukturieren.",
                    auto_fixable=True,
                )
            )
            continue

        # Backtick fence
        if not in_backtick_fence:
            in_backtick_fence = True
            backtick_open_line = i
            open_info = m.group("info").strip()
        else:
            # schließende Zeile (Parser: strip().startswith("```"))
            stripped = line.strip()
            if stripped.startswith("```"):
                in_backtick_fence = False
            else:
                pass

    if in_backtick_fence:
        issues.append(
            Issue(
                severity="blocker",
                category="codeblocks",
                line=backtick_open_line,
                col=1,
                message="Nicht geschlossener fenced Codeblock (``` … fehlende schließende Zeile).",
                fix="Schließende ```-Zeile ergänzen (allein auf der Zeile, optional eingerückt).",
                auto_fixable=False,
            )
        )


def _check_mixed_fences(lines: list[str], issues: list[Issue]) -> None:
    """Öffnet mit ```, schließt mit ~~~ o. Ä."""
    in_fence = False
    open_line = 0
    for i, line in enumerate(lines, start=1):
        m = _FENCE_OPEN.match(line)
        if not m:
            continue
        fence = m.group("fence")
        if fence[0] != "`":
            continue
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```"):
                in_fence = True
                open_line = i
        else:
            if stripped.startswith("~~~"):
                issues.append(
                    Issue(
                        severity="high",
                        category="codeblocks",
                        line=i,
                        col=1,
                        message="Codeblock wurde mit ``` geöffnet, aber mit ~~~ geschlossen (Parser erkennt das nicht).",
                        fix="Schließung auf ``` setzen.",
                        auto_fixable=True,
                    )
                )
                in_fence = False
            elif stripped.startswith("```"):
                in_fence = False


def _check_inline_backticks(lines: list[str], issues: list[Issue]) -> None:
    """Unbalancierte Backticks außerhalb von fenced blocks (heuristisch)."""
    in_fence = False
    for i, line in enumerate(lines, start=1):
        if _FENCE_OPEN.match(line) and line.lstrip().startswith("```"):
            stripped = line.strip()
            if in_fence and stripped.startswith("```"):
                in_fence = False
            elif not in_fence and stripped.startswith("```"):
                in_fence = True
            continue
        if in_fence:
            continue
        # unescaped ` count (vereinfacht)
        cnt = line.count("`")
        if cnt % 2 == 1:
            issues.append(
                Issue(
                    severity="medium",
                    category="codeblocks",
                    line=i,
                    col=None,
                    message="Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.",
                    fix="Backticks paaren oder Zeile in einen Codeblock legen.",
                    auto_fixable=False,
                )
            )


def _check_indented_code_confusion(lines: list[str], issues: list[Issue]) -> None:
    """Tab-eingerückte Codezeilen: Parser frisst Tab anders als Spaces."""
    for i, line in enumerate(lines, start=1):
        if line.startswith("\t") and not line.startswith("\t\t"):
            if _UL.match(line) or _OL.match(line.expandtabs(4)):
                continue
            if line.strip().startswith("```"):
                continue
            issues.append(
                Issue(
                    severity="medium",
                    category="codeblocks",
                    line=i,
                    col=1,
                    message="Zeile beginnt mit Tab — kann als eingerückter Codeblock statt Fließtext geparst werden.",
                    fix="Tabs durch Leerzeichen ersetzen oder Zeile in ```-Fence packen.",
                    auto_fixable=True,
                )
            )


def _check_tables(lines: list[str], issues: list[Issue]) -> None:
    """Tabellen: Spaltenanzahl, Separator, ASCII-Mix."""
    n = len(lines)
    i = 0
    while i < n:
        if not _TABLE_ROW.match(lines[i]):
            i += 1
            continue
        start = i
        block: list[tuple[int, str]] = []
        while i < n and _TABLE_ROW.match(lines[i]):
            block.append((i + 1, lines[i]))
            i += 1
        if len(block) < 2:
            continue

        cell_counts: list[tuple[int, int]] = []
        sep_lines: list[int] = []
        ascii_mixed: list[int] = []

        for ln_no, raw in block:
            cells = _table_cell_parts(raw)
            if _is_separator_row(cells):
                sep_lines.append(ln_no)
                continue
            cell_counts.append((ln_no, len(cells)))
            if re.search(r"\+[-=]+\+", raw) or re.search(r"^\s*\|[\s\-+:]{3,}\|\s*$", raw):
                ascii_mixed.append(ln_no)

        if len(sep_lines) == 0 and len(cell_counts) >= 2:
            issues.append(
                Issue(
                    severity="medium",
                    category="tables",
                    line=block[0][0],
                    col=None,
                    message="Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.",
                    fix="Zwischen Kopf- und Datenzeilen eine |---|---|-Zeile einfügen.",
                    auto_fixable=False,
                )
            )

        counts = [c for _, c in cell_counts]
        if counts and len(set(counts)) > 1:
            issues.append(
                Issue(
                    severity="high",
                    category="tables",
                    line=block[0][0],
                    col=None,
                    message=f"Uneinheitliche Spaltenanzahl in der Tabelle (z. B. {min(counts)} vs. {max(counts)} Zellen).",
                    fix="Jede Zeile auf gleiche Anzahl | … | Zellen bringen.",
                    auto_fixable=False,
                )
            )

        for ln in ascii_mixed:
            issues.append(
                Issue(
                    severity="medium",
                    category="tables",
                    line=ln,
                    col=None,
                    message="Tabellenzeile enthält ASCII-Rahmenzeichen (+---+) — Mischform Markdown/ASCII.",
                    fix="Entweder reine Markdown-Tabelle oder komplett als Codeblock/ASCII-Monospace.",
                    auto_fixable=False,
                )
            )

        if counts and max(counts) >= 10:
            issues.append(
                Issue(
                    severity="low",
                    category="tables",
                    line=block[0][0],
                    col=None,
                    message=f"Sehr breite Tabelle ({max(counts)} Spalten) — in proportionaler GUI evtl. unleserlich.",
                    fix="Spalten reduzieren, umbrechen oder als Codeblock darstellen.",
                    auto_fixable=False,
                )
            )

        # „Sieht aus wie Tabelle“ aber nur eine Zeile mit Pipes
        if len(block) == 2 and len(sep_lines) == 0 and len(cell_counts) == 2:
            pass


def _in_fenced_block(line_index: int, fence_ranges: list[tuple[int, int]]) -> bool:
    for a, b in fence_ranges:
        if a < line_index < b:
            return True
    return False


def _fence_line_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """1-basierte Zeilen: innerhalb (open, close) exklusiv Inhalt."""
    ranges: list[tuple[int, int]] = []
    in_b = False
    open_i = 0
    for i, line in enumerate(lines, start=1):
        if not in_b and line.lstrip().startswith("```"):
            m = _FENCE_OPEN.match(line)
            if m and m.group("fence")[0] == "`":
                in_b = True
                open_i = i
                continue
        elif in_b and line.strip().startswith("```"):
            ranges.append((open_i, i))
            in_b = False
    return ranges


def _check_ascii_unprotected(lines: list[str], issues: list[Issue]) -> None:
    """Mehrere aufeinanderfolgende „ASCII-risk“-Zeilen außerhalb Fence/Indent-Code."""
    if _dominant_ascii_file(lines):
        return
    ranges = _fence_line_ranges(lines)
    n = len(lines)
    run_start: int | None = None
    run_lines: list[int] = []

    def flush_run() -> None:
        nonlocal run_start, run_lines
        if run_start is not None and len(run_lines) >= 3:
            issues.append(
                Issue(
                    severity="medium",
                    category="ascii_blocks",
                    line=run_start,
                    col=None,
                    message=(
                        f"ASCII-/CLI-ähnlicher Block ({len(run_lines)} Zeilen) ohne Fence — "
                        "kann in der GUI als Fließtext mit falscher Breite laufen."
                    ),
                    fix="Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.",
                    auto_fixable=False,
                )
            )
        run_start = None
        run_lines = []

    for i, line in enumerate(lines, start=1):
        if _in_fenced_block(i, ranges):
            flush_run()
            continue
        if line.startswith("    ") or line.startswith("\t"):
            flush_run()
            continue
        if not line.strip():
            flush_run()
            continue
        if _looks_like_ascii_risk_line(line):
            if run_start is None:
                run_start = i
            run_lines.append(i)
        else:
            flush_run()
    flush_run()


def _check_lists(lines: list[str], issues: list[Issue]) -> None:
    """Tabs in Listen, grobe Einrückungssprünge."""
    for i, line in enumerate(lines, start=1):
        if "\t" in line and (_UL.match(line) or _OL.match(line)):
            issues.append(
                Issue(
                    severity="medium",
                    category="lists",
                    line=i,
                    col=1,
                    message="Listenzeile enthält Tab — nach Normalisierung kann Verschachtelung springen.",
                    fix="Tabs durch Leerzeichen (2er/4er Einrückung) ersetzen.",
                    auto_fixable=True,
                )
            )
    # Hinweis: Mehrere „1.“ untereinander ist in CommonMark/GFM üblich (Auto-Nummerierung) — nicht melden.


def _check_headings(lines: list[str], issues: list[Issue]) -> None:
    last_level = 0
    for i, line in enumerate(lines, start=1):
        m = _HEADING_LINE.match(line)
        if not m:
            continue
        hashes, space, rest = m.group(1), m.group(2), m.group(3)
        level = len(hashes)
        if not rest.strip():
            issues.append(
                Issue(
                    severity="high",
                    category="headings",
                    line=i,
                    col=1,
                    message="Leere Überschrift (nur # ohne Text).",
                    fix="Überschriftentext ergänzen oder Zeile entfernen.",
                    auto_fixable=False,
                )
            )
        if last_level > 0 and level > last_level + 1:
            issues.append(
                Issue(
                    severity="medium",
                    category="headings",
                    line=i,
                    col=1,
                    message=f"Sprung in der Überschriftenhierarchie (H{last_level} → H{level}).",
                    fix=f"Zwischenüberschrift H{last_level + 1} einfügen oder Ebene anpassen.",
                    auto_fixable=False,
                )
            )
        last_level = level


def _check_whitespace(raw: str, lines: list[str], issues: list[Issue]) -> None:
    if "\r\n" in raw or "\r" in raw:
        issues.append(
            Issue(
                severity="low",
                category="whitespace",
                line=1,
                col=None,
                message="Datei enthält CRLF oder CR — GUI normalisiert zu LF, Versionsdiffs können stören.",
                fix="Zeilenenden auf LF setzen (Editor oder dos2unix).",
                auto_fixable=True,
            )
        )
    for i, line in enumerate(lines, start=1):
        if "\t" in line:
            issues.append(
                Issue(
                    severity="low",
                    category="whitespace",
                    line=i,
                    col=line.index("\t") + 1,
                    message="Tab-Zeichen in der Zeile.",
                    fix="Tabs durch Spaces ersetzen (expandtabs konsistent mit Projekt).",
                    auto_fixable=True,
                )
            )
        if line.rstrip("\n") != line.rstrip("\n").rstrip(" \t") and line.strip():
            # trailing in code/table can matter
            if line.lstrip().startswith("|") or line.startswith("    "):
                issues.append(
                    Issue(
                        severity="low",
                        category="whitespace",
                        line=i,
                        col=len(line.rstrip("\n").rstrip(" \t")) + 1,
                        message="Trailing Whitespace in Tabellen- oder Code-kritischer Zeile.",
                        fix="Zeilenende bereinigen.",
                        auto_fixable=True,
                    )
                )


def _build_help_topic_index(root: Path) -> dict[str, Path]:
    """
    topic_id / Dateiname ohne .md -> Pfad unter help/
    (entspricht grob HelpIndex / _find_help_article_path).
    """
    out: dict[str, Path] = {}
    hd = root / "help"
    if not hd.is_dir():
        return out
    for p in hd.rglob("*.md"):
        try:
            raw = p.read_text(encoding="utf-8")
        except OSError:
            continue
        stem = p.stem
        for key in (stem, stem.replace("-", "_")):
            out.setdefault(key, p)
        if raw.startswith("---"):
            end = raw.find("\n---", 3)
            if end != -1:
                for line in raw[3:end].split("\n"):
                    if line.startswith("id:"):
                        tid = line.split(":", 1)[1].strip().strip("\"'")
                        if tid:
                            for key in (tid, tid.replace("-", "_")):
                                out.setdefault(key, p)
                        break
    return out


_HELP_ID_LINK = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def _resolve_help_bare_id(
    target: str,
    help_index: dict[str, Path],
) -> Path | None:
    if not _HELP_ID_LINK.match(target):
        return None
    return help_index.get(target) or help_index.get(target.replace("-", "_"))


def _collect_heading_slugs(lines: list[str]) -> set[str]:
    slugs: set[str] = set()
    for line in lines:
        m = _HEADING_LINE.match(line)
        if not m:
            continue
        text = m.group(3).strip()
        if text:
            s = _slug_anchor(text)
            if s:
                slugs.add(s)
    return slugs


def _resolve_local_link(base_file: Path, target: str, root: Path) -> tuple[Path | None, str | None]:
    """Returns (resolved_path_or_none, fragment_or_none)."""
    t = target.strip()
    if not t or t.startswith(("#", "http://", "https://", "mailto:")):
        return None, None
    parsed = urlparse(t)
    path_part = unquote(parsed.path)
    frag = parsed.fragment if parsed.fragment else None
    if not path_part:
        return None, frag
    # absolute from root
    if path_part.startswith("/"):
        cand = (root / path_part.lstrip("/")).resolve()
    else:
        cand = (base_file.parent / path_part).resolve()
    return cand, frag


def _check_links(
    text: str,
    lines: list[str],
    base_file: Path,
    root: Path,
    heading_slugs: set[str],
    issues: list[Issue],
    help_index: dict[str, Path],
) -> None:
    def line_for_offset(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    for m in _MD_LINK.finditer(text):
        target = m.group(2).strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            if target.startswith("#"):
                frag = target[1:].strip()
                if frag:
                    lowered = {h.lower() for h in heading_slugs}
                    if frag.lower() not in lowered and _slug_anchor(frag) not in heading_slugs:
                        issues.append(
                            Issue(
                                severity="low",
                                category="links",
                                line=line_for_offset(m.start()),
                                col=None,
                                message=f"Sprungmarke „#{frag}“ evtl. ohne passende Überschrift in dieser Datei (Slug-Heuristik).",
                                fix="Überschrift oder Anker prüfen (Slug-Konvention).",
                                auto_fixable=False,
                            )
                        )
            continue
        cand, frag = _resolve_local_link(base_file, target, root)
        ln = line_for_offset(m.start())
        if cand is None:
            continue
        path_key = target.split("#", 1)[0].strip()
        try:
            cand.relative_to(root.resolve())
        except ValueError:
            issues.append(
                Issue(
                    severity="high",
                    category="links",
                    line=ln,
                    col=None,
                    message=f"Link-Ziel liegt außerhalb des Projektroots: {target}",
                    fix="Pfad so anpassen, dass er unter dem Repository bleibt.",
                    auto_fixable=False,
                )
            )
            continue
        if not cand.exists():
            # help/*.md: [Titel](topic_id) ohne .md — Auflösung wie HelpIndex / Workspace-Graph
            if (
                "/" not in path_key
                and "\\" not in path_key
                and not path_key.lower().endswith(".md")
            ):
                hid = _resolve_help_bare_id(path_key, help_index)
                if hid is not None and hid.is_file():
                    cand = hid.resolve()
            if not cand.exists():
                try:
                    disp = str(cand.relative_to(root.resolve()))
                except ValueError:
                    disp = str(cand)
                issues.append(
                    Issue(
                        severity="high",
                        category="links",
                        line=ln,
                        col=None,
                        message=f"Lokaler Link-Ziel existiert nicht: {target} (aufgelöst: {disp}).",
                        fix="Pfad korrigieren oder Zieldatei anlegen.",
                        auto_fixable=False,
                    )
                )
                continue
        if frag:
            # andere Datei: keine Heading-Sammlung ohne Lesen — optional shallow
            if cand.suffix.lower() == ".md":
                try:
                    otxt = cand.read_text(encoding="utf-8")
                    oslugs = _collect_heading_slugs(otxt.split("\n"))
                    if frag.lower() not in {x.lower() for x in oslugs} and _slug_anchor(
                        frag.replace("-", " ")
                    ) not in oslugs:
                        issues.append(
                            Issue(
                                severity="medium",
                                category="links",
                                line=ln,
                                col=None,
                                message=f"Datei existiert, Sprungmarke „#{frag}“ in {cand.name} nicht gefunden (heuristisch).",
                                fix="Anker/Überschrift in Zieldatei prüfen.",
                                auto_fixable=False,
                            )
                        )
                except OSError:
                    pass

    for m in _MD_IMAGE.finditer(text):
        target = m.group(2).strip()
        if not target or target.startswith(("http://", "https://", "data:")):
            continue
        cand, _ = _resolve_local_link(base_file, target, root)
        if cand is not None:
            try:
                cand.relative_to(root.resolve())
            except ValueError:
                issues.append(
                    Issue(
                        severity="high",
                        category="links",
                        line=line_for_offset(m.start()),
                        col=None,
                        message=f"Bild-Link liegt außerhalb des Projektroots: {target}",
                        fix="Pfad innerhalb des Repos verwenden.",
                        auto_fixable=False,
                    )
                )
                continue
        if cand and not cand.exists():
            issues.append(
                Issue(
                    severity="high",
                    category="links",
                    line=line_for_offset(m.start()),
                    col=None,
                    message=f"Bild-Link existiert nicht: {target}",
                    fix="Pfad korrigieren oder Asset hinzufügen.",
                    auto_fixable=False,
                )
            )


def analyze_file(path: Path, root: Path, help_index: dict[str, Path]) -> FileResult:
    rel = str(path.resolve().relative_to(root.resolve()))
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return FileResult(
            path=path,
            rel=rel,
            issues=[
                Issue(
                    severity="blocker",
                    category="codeblocks",
                    line=1,
                    col=None,
                    message="Datei ist nicht UTF-8-dekodierbar.",
                    fix="Als UTF-8 speichern.",
                    auto_fixable=False,
                )
            ],
        )

    lines = raw.split("\n")
    issues: list[Issue] = []

    _check_whitespace(raw, lines, issues)
    _check_fences_and_tildas(lines, issues)
    _check_mixed_fences(lines, issues)
    _check_inline_backticks(lines, issues)
    _check_indented_code_confusion(lines, issues)
    _check_tables(lines, issues)
    _check_ascii_unprotected(lines, issues)
    _check_lists(lines, issues)
    _check_headings(lines, issues)

    heading_slugs = _collect_heading_slugs(lines)
    _check_links(raw, lines, path, root, heading_slugs, issues, help_index)

    issues.sort(
        key=lambda i: (
            i.line,
            _severity_rank(i.severity),
            i.category,
            i.message,
        )
    )
    return FileResult(path=path, rel=rel, issues=issues)


def _write_report(
    results: list[FileResult],
    out_path: Path,
    root: Path,
) -> None:
    files_checked = len(results)
    all_issues = [i for r in results for i in r.issues]
    issues_total = len(all_issues)

    def count_sev(s: str) -> int:
        return sum(1 for i in all_issues if i.severity == s)

    blockers = count_sev("blocker")
    high = count_sev("high")
    medium = count_sev("medium")
    low = count_sev("low")

    by_cat: dict[str, list[tuple[FileResult, Issue]]] = defaultdict(list)
    for r in results:
        for i in r.issues:
            by_cat[i.category].append((r, i))

    auto: list[tuple[FileResult, Issue]] = []
    manual: list[tuple[FileResult, Issue]] = []
    for r in results:
        for i in r.issues:
            if i.auto_fixable:
                auto.append((r, i))
            else:
                manual.append((r, i))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines_out: list[str] = [
        "# MARKDOWN VALIDATION REPORT",
        "",
        f"_Generated: {ts} — tool: `tools/validate_markdown_docs.py`_",
        "",
        "## Summary",
        "",
        f"- **files_checked**: {files_checked}",
        f"- **issues_total**: {issues_total}",
        f"- **blockers**: {blockers}",
        f"- **high**: {high}",
        f"- **medium**: {medium}",
        f"- **low**: {low}",
        "",
        "## By File",
        "",
    ]

    for r in results:
        lines_out.append(f"### `{r.rel}`")
        lines_out.append("")
        lines_out.append(f"- **Status**: {r.status}")
        if not r.issues:
            lines_out.append("- Keine festgestellten Probleme in den geprüften Kategorien.")
            lines_out.append("")
            continue
        for i in sorted(r.issues, key=lambda x: (x.line, _severity_rank(x.severity), x.category)):
            col = f", Spalte {i.col}" if i.col is not None else ""
            lines_out.append(
                f"- **{i.severity.upper()}** · `{i.category}` · Zeile {i.line}{col}: {i.message}"
            )
            lines_out.append(f"  - *Empfohlene Korrektur*: {i.fix}")
            if i.auto_fixable:
                lines_out.append("  - *Automatisch normalisierbar*: ja")
        lines_out.append("")

    lines_out.extend(
        [
            "## By Problem Type",
            "",
        ]
    )

    order = (
        "codeblocks",
        "tables",
        "ascii_blocks",
        "lists",
        "headings",
        "whitespace",
        "links",
    )
    for cat in order:
        lines_out.append(f"### {cat}")
        lines_out.append("")
        pairs = by_cat.get(cat, [])
        if not pairs:
            lines_out.append("_Keine Treffer._")
            lines_out.append("")
            continue
        pairs.sort(key=lambda x: (x[0].rel, x[1].line, _severity_rank(x[1].severity)))
        for r, i in pairs:
            col = f":{i.col}" if i.col is not None else ""
            lines_out.append(
                f"- `{r.rel}` Zeile {i.line}{col} — **{i.severity}**: {i.message}"
            )
        lines_out.append("")

    lines_out.extend(
        [
            "## Quick Fix Candidates",
            "",
            "### Automatisch normalisierbar",
            "",
        ]
    )
    if not auto:
        lines_out.append("_Keine._")
    else:
        auto.sort(key=lambda x: (x[0].rel, x[1].line))
        for r, i in auto:
            lines_out.append(f"- `{r.rel}`:{i.line} — {i.category}: {i.message}")
    lines_out.extend(
        [
            "",
            "### Manuell prüfen",
            "",
        ]
    )
    if not manual:
        lines_out.append("_Keine._")
    else:
        manual.sort(key=lambda x: (x[0].rel, x[1].line))
        for r, i in manual:
            lines_out.append(f"- `{r.rel}`:{i.line} — **{i.severity}** / {i.category}: {i.message}")
    lines_out.extend(
        [
            "",
            "## Methodik und Grenzen",
            "",
            "- **Scan**: `README.md`, alle `*.md` unter `docs/`, `help/`, `docs_manual/`, plus weitere `*.md` im Projektroot.",
            "- **GUI-Bezug**: Regeln orientieren an der Markdown-Pipeline (z. B. nur ```-Fences, keine `~~~`; Normalisierung LF/Tabs im Renderer).",
            "- **help/**: Links ohne Pfad/Suffix wie `(chat_overview)` werden als **Topic-IDs** gegen `help/**/*.md` (Frontmatter-`id` bzw. Dateistamm) aufgelöst — wie im Hilfe-Index.",
            "- **Nicht geprüft**: Reference-Links `[x][ref]`, rohes HTML, benutzerdefinierte Anker außerhalb von `#`-Überschriften-Slugs.",
            "- **Erneut ausführen**: `python3 tools/validate_markdown_docs.py` überschreibt diesen Report deterministisch.",
            "",
        ]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines_out), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project Markdown for GUI rendering risks.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Report path (default: {DEFAULT_REPORT})",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="No stdout summary")
    args = parser.parse_args()

    root = PROJECT_ROOT
    files = _collect_markdown_files(root)
    help_index = _build_help_topic_index(root)
    results = [analyze_file(p, root, help_index) for p in files]

    _write_report(results, args.output, root)

    all_i = [i for r in results for i in r.issues]
    blockers = sum(1 for i in all_i if i.severity == "blocker")

    if not args.quiet:
        print(f"Checked {len(files)} files, {len(all_i)} issues, {blockers} blockers.")
        print(f"Report: {args.output}")

    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
