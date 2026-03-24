"""
Theme-Module unter ``app/gui/themes/`` bleiben reine GUI-Theme-Infrastruktur:

Keine Imports aus ``app.services``, ``app.ui_application`` oder ``app.gui.domains``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

THEMES_PKG = APP_ROOT / "gui" / "themes"

FORBIDDEN_PREFIXES = (
    "app.services",
    "app.ui_application",
    "app.gui.domains",
)


def _forbidden_imports(tree: ast.Module) -> list[str]:
    bad: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0:3]
                m = ".".join(mod) if len(mod) >= 2 else alias.name
                for pref in FORBIDDEN_PREFIXES:
                    if alias.name == pref or alias.name.startswith(pref + "."):
                        bad.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for pref in FORBIDDEN_PREFIXES:
                if mod == pref or mod.startswith(pref + "."):
                    bad.append(mod)
    return bad


@pytest.mark.architecture
def test_gui_themes_packages_avoid_services_and_ui_application_and_domains() -> None:
    offenders: list[str] = []
    for path in sorted(THEMES_PKG.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        hits = _forbidden_imports(tree)
        if hits:
            rel = path.relative_to(APP_ROOT)
            offenders.append(f"{rel}: {sorted(set(hits))}")
    assert not offenders, "Forbidden imports in app/gui/themes:\n" + "\n".join(offenders)
