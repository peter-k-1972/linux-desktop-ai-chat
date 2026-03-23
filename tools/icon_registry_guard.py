#!/usr/bin/env python3
"""
Icon Registry Guard — Konsistenz REGISTRY_TO_RESOURCE ↔ Dateisystem + Nav-Konflikte.

Prüft:
  - jede Registry-ID hat existierende SVG unter resources/icons/
  - Kategorie ∈ Taxonomie
  - keine doppelten Dateizuordnungen (gleiche Datei für zwei IDs)
  - verwaiste SVGs (kein Registry-Eintrag)
  - harte Konfliktregeln (nav_mapping: deployment → deploy, markdown demo → sparkles, …)

Exit: 0 = ok, 1 = Violations (inkl. fehlender Dateien / Konflikt), 2 = Umgebungsfehler
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_CATEGORIES: frozenset[str] = frozenset(
    {
        "navigation",
        "objects",
        "actions",
        "states",
        "ai",
        "workflow",
        "data",
        "monitoring",
        "system",
    }
)


def _setup_import_path() -> Path:
    base = ROOT
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    return base


def collect_registry_issues(base: Path) -> tuple[list[str], list[str], list[str]]:
    """
    Returns: (violations, warnings, orphan_svgs_relative)
    """
    _setup_import_path()
    from app.gui.icons.icon_registry import REGISTRY_TO_RESOURCE
    from app.gui.icons.nav_mapping import OPS_WORKSPACE_ICONS, RD_WORKSPACE_ICONS
    from app.gui.icons.registry import IconRegistry

    violations: list[str] = []
    warnings: list[str] = []
    icons_root = base / "resources" / "icons"

    if not icons_root.is_dir():
        return ([f"Fehlt: {icons_root}"], [], [])

    path_to_ids: dict[str, list[str]] = defaultdict(list)
    for rid, (cat, fname) in REGISTRY_TO_RESOURCE.items():
        if cat not in ALLOWED_CATEGORIES:
            violations.append(f"Registry «{rid}»: unbekannte Kategorie «{cat}»")
        rel = f"{cat}/{fname}"
        full = icons_root / cat / fname
        path_to_ids[rel].append(rid)
        if not full.is_file():
            violations.append(f"Registry «{rid}»: fehlende Datei resources/icons/{rel}")

    for rel, ids in path_to_ids.items():
        if len(ids) > 1:
            violations.append(f"Doppelte Zuordnung resources/icons/{rel} → {ids}")

    # Orphans
    registered_paths = set(path_to_ids.keys())
    orphans: list[str] = []
    for p in sorted(icons_root.rglob("*.svg")):
        try:
            rel = p.relative_to(icons_root).as_posix()
        except ValueError:
            continue
        if rel not in registered_paths:
            orphans.append(rel)

    if orphans:
        warnings.append(f"Orphan-SVGs (nicht in REGISTRY_TO_RESOURCE): {len(orphans)} Datei(en)")
        for o in orphans[:50]:
            warnings.append(f"  orphan: resources/icons/{o}")
        if len(orphans) > 50:
            warnings.append(f"  … und {len(orphans) - 50} weitere")

    # Konflikt-Detector (1 Icon = 1 Bedeutung an kritischen Stellen)
    dep = OPS_WORKSPACE_ICONS.get("operations_deployment")
    if dep != IconRegistry.DEPLOY:
        violations.append(
            f"Konflikt: operations_deployment muss auf «{IconRegistry.DEPLOY}» zeigen, ist «{dep}»"
        )
    md = RD_WORKSPACE_ICONS.get("rd_markdown_demo")
    if md != IconRegistry.SPARKLES:
        violations.append(
            f"Konflikt: rd_markdown_demo muss auf «{IconRegistry.SPARKLES}» zeigen, ist «{md}»"
        )
    qa_cockpit = RD_WORKSPACE_ICONS.get("rd_qa_cockpit")
    if qa_cockpit == IconRegistry.SHIELD:
        violations.append(
            "Konflikt: rd_qa_cockpit darf nicht «shield» sein (Runtime vs Governance) — erwarte «qa_runtime»"
        )

    # Dokumentation vs. Code (ICON_MAPPING / Kanon)
    mp = base / "docs" / "design" / "ICON_MAPPING.md"
    if mp.is_file():
        md = mp.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\|\s*Deployment\s*\|\s*`data_stores`", md):
            violations.append("ICON_MAPPING.md: Deployment darf nicht auf data_stores zeigen")
        if re.search(r"\|\s*Markdown Demo\s*\|\s*`logs`", md):
            violations.append("ICON_MAPPING.md: Markdown-Demo darf nicht logs recyceln (→ sparkles)")

    return violations, warnings, orphans


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Icon Registry Guard")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--fail-on-orphans", action="store_true", help="Orphans als Violation (Exit 1)")
    args = ap.parse_args(argv)
    base = args.root.resolve()
    viol, warn, orphans = collect_registry_issues(base)
    if args.fail_on_orphans and orphans:
        viol.append(f"Orphan-SVGs (--fail-on-orphans): {len(orphans)}")

    for w in warn:
        print(w, file=sys.stderr)

    if viol:
        for v in viol:
            print(v, file=sys.stderr)
        return 1
    print(f"OK: icon_registry_guard ({len(orphans)} orphans nur als Warnung)" if orphans else "OK: icon_registry_guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
