#!/usr/bin/env python3
"""
Zentrales Markdown-Quality-Gate: Validierung, Normalisierungs-Check, Render-Stabilität, Link-Logik.

Deterministisch, rein lokal (keine Netzwerk-Calls).

Exit-Codes:
  0 — PASS
  1 — PASS_WITH_WARNINGS
  2 — FAIL

Usage:
  python3 tools/run_markdown_quality_gate.py [--quiet] [--json PATH]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# --- Zentrale Einstiegspunkte (strengere Link-Regeln) ---
ENTRY_POINT_RELS: frozenset[str] = frozenset(
    {
        "README.md",
        "docs/README.md",
        "help/getting_started/introduction.md",
        "docs_manual/README.md",
    }
)

# Kritische Demodateien: Pipeline darf nicht crashen
DEMO_DIR = PROJECT_ROOT / "app" / "resources" / "demo_markdown"

# CI-Profil: High (nicht auto-fixbar) nur in produktnahen Pfaden als FAIL — Rest → WARN
_CI_HIGH_FAIL_PREFIXES: tuple[str, ...] = (
    "help/",
    "docs_manual/",
    "app/resources/demo_markdown/",
    "docs/01_product_overview/",
    "docs/02_user_manual/",
)
_CI_HIGH_FAIL_EXACT: frozenset[str] = frozenset(("README.md", "docs/README.md"))

# Erwartete Render-Segment-Typen (mindestens einer pro Datei, außer broken_markdown)
RENDER_EXPECTATIONS: dict[str, frozenset[str]] = {
    "app/resources/demo_markdown/code_blocks.md": frozenset({"code_block"}),
    "app/resources/demo_markdown/ascii_tree.md": frozenset({"code_block", "ascii_block"}),
    "app/resources/demo_markdown/ascii_boxes.md": frozenset({"code_block", "ascii_block"}),
    "app/resources/demo_markdown/cli_output.md": frozenset({"code_block"}),
    "app/resources/demo_markdown/mixed.md": frozenset(
        {"code_block", "ascii_block", "table_block", "preformatted_block"}
    ),
    "docs/implementation/MARKDOWN_BLOCK_VALIDATION.md": frozenset(
        {"table_block", "preformatted_block"}
    ),
}


@dataclass
class GateCounters:
    files_checked: int = 0
    errors: int = 0
    warnings: int = 0
    safe_fix_candidates: int = 0
    parser_failures: int = 0
    messages: list[str] = field(default_factory=list)

    def add_line(self, level: str, text: str) -> None:
        self.messages.append(f"[{level}]  {text}")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Kann Modul nicht laden: {path}")
    mod = importlib.util.module_from_spec(spec)
    # Dataclasses erfordert sys.modules-Eintrag vor exec_module
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _collect_extended_markdown_files(root: Path, vmod) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for p in vmod._collect_markdown_files(root):
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    demo = root / "app" / "resources" / "demo_markdown"
    if demo.is_dir():
        for p in sorted(demo.glob("*.md")):
            rp = p.resolve()
            if rp not in seen:
                seen.add(rp)
                out.append(p)
    out.sort(key=lambda x: str(x.resolve()).lower())
    return out


def _issue_is_fail(
    rel: str,
    severity: str,
    auto_fixable: bool,
    category: str,
) -> bool:
    if severity == "blocker":
        return True
    if severity == "high":
        return not auto_fixable
    if rel in ENTRY_POINT_RELS and category == "links" and severity == "medium":
        return True
    return False


def _issue_is_warn(
    rel: str,
    severity: str,
    auto_fixable: bool,
    category: str,
) -> bool:
    if _issue_is_fail(rel, severity, auto_fixable, category):
        return False
    if severity == "low":
        return True
    if severity == "medium":
        return True
    if severity == "high" and auto_fixable:
        return True
    return False


def _ci_high_non_auto_counts_as_fail(rel: str) -> bool:
    r = rel.replace("\\", "/")
    if r in _CI_HIGH_FAIL_EXACT:
        return True
    return any(r.startswith(p) for p in _CI_HIGH_FAIL_PREFIXES)


def _effective_validator_fail(rel: str, severity: str, auto_fixable: bool, category: str, profile: str) -> bool:
    if not _issue_is_fail(rel, severity, auto_fixable, category):
        return False
    if profile == "ci" and severity == "high" and not auto_fixable and not _ci_high_non_auto_counts_as_fail(rel):
        return False
    return True


def _run_render_stability(
    paths: Iterable[Path],
    counters: GateCounters,
    quiet: bool,
) -> None:
    root = PROJECT_ROOT.resolve()
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from app.gui.shared.markdown.markdown_api import render_segments
    except ImportError as e:
        counters.parser_failures += 1
        counters.add_line("FAIL", f"Import der Markdown-Pipeline fehlgeschlagen: {e}")
        return

    for path in paths:
        rel = str(path.resolve().relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            counters.errors += 1
            counters.add_line("FAIL", f"{rel}: Datei nicht lesbar: {e}")
            continue
        try:
            segments = render_segments(text, promote_ascii=True)
        except Exception as e:
            counters.parser_failures += 1
            counters.errors += 1
            counters.add_line("FAIL", f"{rel}: Parser/Renderer-Exception: {e!r}")
            continue

        kinds = {getattr(s, "kind", type(s).__name__) for s in segments}
        if rel.endswith("broken_markdown.md"):
            if not (kinds & frozenset({"malformed_block", "code_block"})):
                counters.errors += 1
                counters.add_line(
                    "FAIL",
                    f"{rel}: erwartet malformed_block oder code_block für defektes Demo, "
                    f"bekommen: {sorted(kinds)}",
                )
            continue

        expected = RENDER_EXPECTATIONS.get(rel.replace("\\", "/"))
        if expected is not None:
            if not (kinds & expected):
                counters.errors += 1
                counters.add_line(
                    "FAIL",
                    f"{rel}: erwartete Segment-Typen aus {sorted(expected)}, "
                    f"bekommen: {sorted(kinds)}",
                )


def run_gate(*, quiet: bool = False, profile: str = "strict") -> tuple[str, dict[str, Any], GateCounters]:
    vmod = _load_module("markdown_gate_validate", SCRIPT_DIR / "validate_markdown_docs.py")
    nmod = _load_module("markdown_gate_normalize", SCRIPT_DIR / "normalize_markdown_docs.py")

    root = PROJECT_ROOT
    files = _collect_extended_markdown_files(root, vmod)
    help_index = vmod._build_help_topic_index(root)

    counters = GateCounters()
    counters.files_checked = len(files)

    demo_resolved = DEMO_DIR.resolve()
    validator_results: list = []
    for p in files:
        # Absichtlich kaputter Demoinhalt — nur Render-Stabilität, keine Struktur-Blocker
        if p.resolve().parent == demo_resolved and p.name == "broken_markdown.md":
            rel = str(p.resolve().relative_to(root.resolve())).replace("\\", "/")
            validator_results.append(vmod.FileResult(path=p, rel=rel, issues=[]))
        else:
            validator_results.append(vmod.analyze_file(p, root, help_index))

    for vr in validator_results:
        rel = vr.rel.replace("\\", "/")
        for issue in vr.issues:
            eff_fail = _effective_validator_fail(
                rel, issue.severity, issue.auto_fixable, issue.category, profile
            )
            if eff_fail:
                counters.errors += 1
                col = f":{issue.col}" if issue.col is not None else ""
                counters.add_line(
                    "FAIL",
                    f"{rel}:{issue.line}{col} [{issue.category}/{issue.severity}] {issue.message}",
                )
            elif _issue_is_fail(rel, issue.severity, issue.auto_fixable, issue.category) and profile == "ci":
                counters.warnings += 1
                if not quiet:
                    col = f":{issue.col}" if issue.col is not None else ""
                    counters.add_line(
                        "WARN",
                        f"{rel}:{issue.line}{col} [{issue.category}/{issue.severity}] "
                        f"(CI-Profil: High außerhalb produktnaher Pfade) {issue.message}",
                    )
            elif _issue_is_warn(rel, issue.severity, issue.auto_fixable, issue.category):
                counters.warnings += 1
                if not quiet:
                    col = f":{issue.col}" if issue.col is not None else ""
                    counters.add_line(
                        "WARN",
                        f"{rel}:{issue.line}{col} [{issue.category}/{issue.severity}] {issue.message}",
                    )

    # --- Normalizer: Check-Modus (safe-fix Kandidaten) ---
    for path in files:
        if path.resolve().parent == demo_resolved and path.name == "broken_markdown.md":
            continue
        rel = str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        normalized, _stats = nmod.normalize_markdown_content(raw)
        if normalized != raw:
            counters.safe_fix_candidates += 1
            if not quiet:
                counters.add_line(
                    "WARN",
                    f"{rel}: safe-normalisierbar (tools/normalize_markdown_docs.py --fix-safe)",
                )

    # --- Render-Stabilität: Demos + Tabellen-Referenzdokument ---
    stability_paths: list[Path] = []
    if DEMO_DIR.is_dir():
        stability_paths.extend(sorted(DEMO_DIR.glob("*.md")))
    mdoc = root / "docs" / "implementation" / "MARKDOWN_BLOCK_VALIDATION.md"
    if mdoc.is_file():
        stability_paths.append(mdoc)
    _run_render_stability(stability_paths, counters, quiet)

    fail = counters.errors > 0 or counters.parser_failures > 0
    has_warn = counters.warnings > 0 or counters.safe_fix_candidates > 0

    if fail:
        final_status = "FAIL"
    elif has_warn:
        final_status = "PASS_WITH_WARNINGS"
    else:
        final_status = "PASS"

    summary = {
        "files_checked": counters.files_checked,
        "errors": counters.errors,
        "warnings": counters.warnings,
        "safe_fix_candidates": counters.safe_fix_candidates,
        "parser_failures": counters.parser_failures,
        "final_status": final_status,
        "profile": profile,
    }

    if not quiet and final_status == "PASS":
        counters.add_line("PASS", "Markdown validation clean")

    return final_status, summary, counters


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown Quality Gate (lokal, deterministisch).")
    parser.add_argument("--quiet", "-q", action="store_true", help="Nur Summary, keine WARN-Zeilen")
    parser.add_argument("--json", type=Path, default=None, help="Summary als JSON schreiben")
    parser.add_argument(
        "--profile",
        choices=("strict", "ci"),
        default="strict",
        help="strict: alle High (nicht auto) sind FAIL. ci: High nur in Help, Handbuch, Demos, README, docs/01–02.",
    )
    args = parser.parse_args()

    final_status, summary, counters = run_gate(quiet=args.quiet, profile=args.profile)

    for line in counters.messages:
        print(line)

    print("")
    print("--- Markdown Quality Gate — Summary ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("")

    if args.json is not None:
        payload = {
            **summary,
            "generated": datetime.now(timezone.utc).isoformat(),
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if final_status == "FAIL":
        return 2
    if final_status == "PASS_WITH_WARNINGS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
