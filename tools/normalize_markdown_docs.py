#!/usr/bin/env python3
"""
Kontrollierter Markdown-Normalizer: nur sichere, idempotente Korrekturen.

Kein semantisches Umschreiben; Monospace-/ASCII-sensible Zeilen bleiben unangetastet.

Usage:
  python3 tools/normalize_markdown_docs.py --check
  python3 tools/normalize_markdown_docs.py --fix-safe [--dry-run] [--diff]
  python3 tools/normalize_markdown_docs.py --report [--report-md PATH] [--report-json PATH]
  python3 tools/normalize_markdown_docs.py --fix-safe --report

Standard-Report: docs/MARKDOWN_NORMALIZATION_REPORT.md

Exit-Codes:
  --check: 1 wenn Normalisierung nötig wäre und nicht in demselben Lauf per --fix-safe
           (ohne --dry-run) geschrieben wurde; sonst 0
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_MD_REPORT = PROJECT_ROOT / "docs" / "MARKDOWN_NORMALIZATION_REPORT.md"

# Abgleich mit GUI: nur Backtick-Fences als Codekörper schützen
_FENCE_OPEN = re.compile(r"^(\s*)(`{3,})([^`]*)$")
_FENCE_CLOSE = re.compile(r"^(\s*)(`{3,})\s*$")
_UL = re.compile(r"^(\s*)[-*+]\s+")
_OL = re.compile(r"^(\s*)\d+\.\s+")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_CLI_LINE = re.compile(
    r"^\s*(\$\s|#\s|>\s|C:\\|INFO|WARN|ERROR|ERR!|Traceback|at\s+\w|^\[\w+\]|docker\s|kubectl\s|npm\s|pip\s)",
    re.IGNORECASE,
)
_TREE_OR_TABLE = re.compile(r"^[\s│├└┌┐┘┬┴┼─]+\S")
_BOX_LINE = re.compile(r"^[\s\-+|.:=#oO/\\]{6,}$")
_STRUCTURE_CHARS = frozenset("|+-/\\_=<>[]()")

MAX_OUTSIDE_BLANK_STREAK = 2


def _load_validator():
    name = "validate_markdown_docs"
    vp = SCRIPT_DIR / "validate_markdown_docs.py"
    spec = importlib.util.spec_from_file_location(name, vp)
    if not spec or not spec.loader:
        raise RuntimeError("validate_markdown_docs.py nicht gefunden")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _line_structure_density(s: str) -> float:
    if not s:
        return 0.0
    hits = sum(1 for c in s if c in _STRUCTURE_CHARS or c in "│├└┌┐┘─")
    return hits / len(s)


def _looks_like_ascii_risk_line(s: str) -> bool:
    s = s.rstrip()
    if not s or len(s) < 4:
        return False
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


def _dominant_ascii_file(lines: list[str]) -> bool:
    ne = [ln for ln in lines if ln.strip()]
    if len(ne) < 12:
        return False
    hits = sum(1 for ln in ne if _looks_like_ascii_risk_line(ln))
    return hits / len(ne) >= 0.42


def _is_list_line(line: str) -> bool:
    e = line.expandtabs(4)
    return bool(_UL.match(e) or _OL.match(e))


@dataclass
class FixStats:
    line_endings: int = 0
    tabs_to_spaces: int = 0
    trailing_removed: int = 0
    blank_lines_collapsed: int = 0
    fence_blank_inserted: int = 0
    fence_ticks_normalized: int = 0

    def any(self) -> bool:
        return any(
            (
                self.line_endings,
                self.tabs_to_spaces,
                self.trailing_removed,
                self.blank_lines_collapsed,
                self.fence_blank_inserted,
                self.fence_ticks_normalized,
            )
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "line_endings": self.line_endings,
            "tabs_to_spaces": self.tabs_to_spaces,
            "trailing_removed": self.trailing_removed,
            "blank_lines_collapsed": self.blank_lines_collapsed,
            "fence_blank_inserted": self.fence_blank_inserted,
            "fence_ticks_normalized": self.fence_ticks_normalized,
        }


@dataclass
class FileNormalizeResult:
    rel: str
    path: Path
    changed: bool
    stats: FixStats
    manual_notes: list[str] = field(default_factory=list)
    diff_text: str = ""


def _scan_fence_body_mask(lines: list[str]) -> list[bool]:
    """True = Zeile gehört zum Codekörper innerhalb ``` … ``` (ohne die Fence-Zeilen)."""
    in_body = False
    mask = [False] * len(lines)
    for i, line in enumerate(lines):
        s = line.strip()
        if not in_body:
            m = _FENCE_OPEN.match(line)
            if m and len(m.group(2)) >= 3:
                in_body = True
            continue
        if _FENCE_CLOSE.match(line):
            in_body = False
            continue
        mask[i] = True
    return mask


def _normalize_fence_ticks(lines: list[str], stats: FixStats) -> None:
    """Nur Backtick-Fences; Länge > 3 auf genau 3, wenn Rest der Zeile unkontrovers."""
    in_body = False
    for i, line in enumerate(lines):
        if not in_body:
            m = _FENCE_OPEN.match(line)
            if m and len(m.group(2)) >= 3:
                indent, ticks, rest = m.group(1), m.group(2), m.group(3)
                if len(ticks) > 3:
                    lines[i] = indent + "```" + rest
                    stats.fence_ticks_normalized += 1
                in_body = True
            continue
        m = _FENCE_CLOSE.match(line)
        if m:
            indent, ticks = m.group(1), m.group(2)
            if len(ticks) > 3:
                lines[i] = indent + "```"
                stats.fence_ticks_normalized += 1
            in_body = False


def _prose_safe_line(
    line: str,
    in_body: bool,
    ascii_protect: bool,
    stats: FixStats,
) -> str:
    if in_body:
        return line
    if ascii_protect:
        return line
    out = line
    if "\t" in out:
        expanded = out.expandtabs(4)
        if expanded != out:
            stats.tabs_to_spaces += 1
        out = expanded
    stripped = out.rstrip(" \t")
    if stripped != out:
        stats.trailing_removed += 1
    return stripped


def _insert_fence_blanks(lines: list[str], stats: FixStats) -> None:
    """Leerzeile vor erstem ```-Open (nach Prosa) und nach ```-Close, wenn eindeutig."""
    i = 0
    in_body = False
    while i < len(lines):
        line = lines[i]
        if not in_body:
            m = _FENCE_OPEN.match(line)
            if m and len(m.group(2)) >= 3:
                if i > 0 and lines[i - 1].strip() != "":
                    lines.insert(i, "")
                    stats.fence_blank_inserted += 1
                    i += 1
                in_body = True
            i += 1
            continue
        if _FENCE_CLOSE.match(line):
            in_body = False
            j = i + 1
            if j < len(lines) and lines[j].strip() != "":
                lines.insert(j, "")
                stats.fence_blank_inserted += 1
            i += 1
            continue
        i += 1


def _collapse_outside_blank_runs(lines: list[str], body_mask: list[bool], stats: FixStats) -> None:
    out: list[str] = []
    run = 0
    for i, line in enumerate(lines):
        if body_mask[i]:
            run = 0
            out.append(line)
            continue
        if line.strip() == "":
            run += 1
            if run <= MAX_OUTSIDE_BLANK_STREAK:
                out.append(line)
            else:
                stats.blank_lines_collapsed += 1
        else:
            run = 0
            out.append(line)
    lines.clear()
    lines.extend(out)


def _apply_prose_whitespace(lines: list[str], stats: FixStats) -> None:
    """Tabs/Trailing außerhalb Fence-Körper und außerhalb ASCII-sensibler Zeilen."""
    in_body = False
    for i, line in enumerate(lines):
        if not in_body:
            m = _FENCE_OPEN.match(line)
            if m and len(m.group(2)) >= 3:
                lines[i] = _prose_safe_line(line, False, False, stats)
                in_body = True
                continue
            asc = _looks_like_ascii_risk_line(line)
            lines[i] = _prose_safe_line(line, False, asc, stats)
            continue
        if _FENCE_CLOSE.match(line):
            lines[i] = _prose_safe_line(line, False, False, stats)
            in_body = False
            continue
        # Fence-Körper: unverändert lassen


def _stabilize_list_tabs(lines: list[str], stats: FixStats) -> None:
    """Nur Zeilen mit Listen-Markern: Tabs → Spaces (außerhalb Fence-Körper, nicht ASCII)."""
    body_mask = _scan_fence_body_mask(lines)
    for i, line in enumerate(lines):
        if body_mask[i]:
            continue
        if _looks_like_ascii_risk_line(line):
            continue
        if not _is_list_line(line):
            continue
        if "\t" not in line:
            continue
        ex = line.expandtabs(4)
        if ex != line:
            lines[i] = ex
            stats.tabs_to_spaces += 1


def normalize_markdown_content(raw: str) -> tuple[str, FixStats]:
    """
    Wendet sichere Transformationen an. Idempotent für typische Eingaben.
    """
    stats = FixStats()
    if "\r" in raw:
        stats.line_endings += 1
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    if _dominant_ascii_file(lines):
        out = "\n".join(lines)
        if not out.endswith("\n"):
            out += "\n"
            stats.line_endings += 1
        return out, stats

    _normalize_fence_ticks(lines, stats)
    _apply_prose_whitespace(lines, stats)

    body_mask = _scan_fence_body_mask(lines)
    _collapse_outside_blank_runs(lines, body_mask, stats)
    body_mask = _scan_fence_body_mask(lines)
    _insert_fence_blanks(lines, stats)

    _stabilize_list_tabs(lines, stats)

    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    return out, stats


def _validator_manual_findings(vmod, path: Path, root: Path, help_index: dict) -> list[str]:
    r = vmod.analyze_file(path, root, help_index)
    out: list[str] = []
    for i in r.issues:
        sev = i.severity.upper()
        out.append(f"[{sev}] Zeile {i.line} · `{i.category}`: {i.message}")
    return out


def _write_md_report(
    results: list[FileNormalizeResult],
    manual_by_file: dict[str, list[str]],
    out_path: Path,
    mode_label: str,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    changed = [r for r in results if r.changed]
    lines_o: list[str] = [
        "# MARKDOWN NORMALIZATION REPORT",
        "",
        f"_Generated: {ts} — `tools/normalize_markdown_docs.py`_",
        "",
        "## Summary",
        "",
        f"- **Modus**: {mode_label}",
        f"- **Dateien gesamt**: {len(results)}",
        f"- **Geändert**: {len(changed)}",
        "",
        "## Geänderte Dateien und Korrekturarten",
        "",
    ]
    if not changed:
        lines_o.append("_Keine Änderungen (bereits normalisiert oder nur manuelle Hinweise)._")
        lines_o.append("")
    else:
        for r in sorted(changed, key=lambda x: x.rel):
            lines_o.append(f"### `{r.rel}`")
            lines_o.append("")
            d = r.stats.to_dict()
            for k, v in d.items():
                if v:
                    lines_o.append(f"- **{k}**: {v}")
            lines_o.append("")

    lines_o.extend(
        [
            "## Manuell offene Fälle (nicht auto-normalisiert)",
            "",
            "Die folgenden Punkte stammen aus dem Renderer-Validator (`validate_markdown_docs.py`) "
            "und betreffen u. a. Tabellen, ASCII/CLI-Blöcke, Links, Überschriften — **kein** blindes Fix.",
            "",
        ]
    )
    has_manual = False
    for rel in sorted(manual_by_file):
        items = manual_by_file[rel]
        if not items:
            continue
        has_manual = True
        lines_o.append(f"### `{rel}`")
        lines_o.append("")
        for item in items[:200]:
            lines_o.append(f"- {item}")
        if len(items) > 200:
            lines_o.append(f"- _… {len(items) - 200} weitere Einträge gekürzt_")
        lines_o.append("")
    if not has_manual:
        lines_o.append("_Keine Validator-Hinweise (oder alle Dateien ohne Issues)._")
        lines_o.append("")

    lines_o.extend(
        [
            "## Idempotenz und Schutzregeln",
            "",
            "- Wiederholtes Ausführen von `--fix-safe` soll keine neue Drift erzeugen.",
            "- **Geschützt**: Codekörper innerhalb ` ``` ` … ` ``` `; Zeilen mit ASCII-/CLI-/Diagramm-Heuristik; "
            "Dateien mit überwiegend strukturiertem ASCII (z. B. Tree-Dumps) — dort nur Zeilenenden.",
            "- **Nicht automatisch**: unklare Tabellen, Pseudotabellen, kaputte Links, Heading-Sprünge (siehe Validator).",
            "",
        ]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines_o), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sicherer Markdown-Normalizer für Projekt-Dokumentation."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Prüfen, ob Normalisierung nötig wäre (schreibt nichts). Exit 1 bei Abweichung.",
    )
    parser.add_argument(
        "--fix-safe",
        action="store_true",
        help="Sichere Korrekturen in Dateien schreiben (außer mit --dry-run).",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Report-Datei(en) erzeugen.",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=None,
        help=f"Markdown-Report (Default: {DEFAULT_MD_REPORT})",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional: JSON-Report-Pfad.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mit --fix-safe: keine Dateien schreiben, nur anzeigen.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Unified Diff für geänderte Dateien auf stdout.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Weniger Konsolen-Ausgabe.",
    )
    args = parser.parse_args()

    if not args.check and not args.fix_safe and not args.report:
        parser.error("Mindestens eines von --check, --fix-safe, --report angeben.")

    root = PROJECT_ROOT
    vmod = _load_validator()
    files = vmod._collect_markdown_files(root)
    need_manual = bool(args.report or args.report_json)
    help_index = vmod._build_help_topic_index(root) if need_manual else {}

    results: list[FileNormalizeResult] = []
    manual_by_file: dict[str, list[str]] = {}

    for path in files:
        rel = str(path.resolve().relative_to(root.resolve()))
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            if not args.quiet:
                print(f"Skip {rel}: {e}", file=sys.stderr)
            continue

        normalized, stats = normalize_markdown_content(raw)
        changed = normalized != raw
        manual: list[str] = []
        if need_manual:
            manual = _validator_manual_findings(vmod, path, root, help_index)
            if manual:
                manual_by_file[rel] = manual

        diff_text = ""
        if changed and args.diff:
            diff_text = "".join(
                unified_diff(
                    raw.splitlines(keepends=True),
                    normalized.splitlines(keepends=True),
                    fromfile=f"a/{rel}",
                    tofile=f"b/{rel}",
                )
            )

        fr = FileNormalizeResult(
            rel=rel,
            path=path,
            changed=changed,
            stats=stats,
            manual_notes=manual if need_manual else [],
            diff_text=diff_text,
        )
        results.append(fr)

        if changed and args.diff and diff_text and not args.quiet:
            sys.stdout.write(diff_text)

        if args.fix_safe and changed and not args.dry_run:
            path.write_text(normalized, encoding="utf-8", newline="\n")

    report_md_path = args.report_md if args.report_md is not None else DEFAULT_MD_REPORT
    mode_bits: list[str] = []
    if args.check:
        mode_bits.append("--check")
    if args.fix_safe:
        mode_bits.append("--fix-safe" + (" --dry-run" if args.dry_run else ""))
    if args.report or args.report_md is not None:
        mode_bits.append("--report")
    mode_label = ", ".join(mode_bits) if mode_bits else "—"

    if args.report or args.report_md is not None:
        _write_md_report(results, manual_by_file, report_md_path, mode_label)
        if not args.quiet:
            print(f"Markdown-Report: {report_md_path}")

    if args.report_json:
        payload: dict[str, Any] = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "files": [
                {
                    "path": r.rel,
                    "changed": r.changed,
                    "fixes": r.stats.to_dict(),
                }
                for r in results
            ],
            "manual_findings": {k: v[:500] for k, v in manual_by_file.items()},
        }
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        if not args.quiet:
            print(f"JSON-Report: {args.report_json}")

    would_change = sum(1 for r in results if r.changed)
    if not args.quiet:
        print(
            f"Fertig: {len(results)} Dateien, "
            f"{'würden geändert' if args.dry_run and args.fix_safe else 'geändert' if args.fix_safe else 'zu prüfen'}: {would_change}"
        )

    if args.check and would_change:
        # Mit echtem --fix-safe wurde bereits normalisiert — dann kein Fehlercode mehr nötig.
        if not (args.fix_safe and not args.dry_run):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
