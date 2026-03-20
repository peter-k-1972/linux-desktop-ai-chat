"""
Architektur-Guard: gui darf nicht ui importieren.

Regel: app/gui/ darf keine Module aus app/ui/ importieren.
app/ui wurde in gui migriert; dieser Guard verhindert Drift (Neuaufbau von app.ui).

Referenz: docs/04_architecture/ARCHITECTURE_GUARD_RULES.md
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import APP_ROOT

# Bekannte gui->ui Verletzungen (Legacy, Migration ausstehend).
# Phase C: chat_widget umgestellt; keine bekannten Verletzungen mehr.
KNOWN_GUI_UI_VIOLATIONS = frozenset()


def _extract_imported_modules(file_path: Path) -> list[str]:
    """Extrahiert alle importierten Modulnamen (app.*) aus einer Python-Datei."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app."):
                    imported.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                imported.append(node.module)
    return imported


def test_gui_layer_does_not_import_ui_layer():
    """Kein Modul unter app/gui/ darf app.ui.* importieren (außer bekannte Legacy)."""
    gui_root = APP_ROOT / "gui"
    if not gui_root.exists():
        pytest.skip("app/gui/ nicht vorhanden")

    violations = []
    for path in gui_root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        if rel_str in KNOWN_GUI_UI_VIOLATIONS:
            continue
        for mod in _extract_imported_modules(path):
            if mod.startswith("app.ui."):
                violations.append((rel_str, mod))

    assert not violations, (
        f"gui darf nicht ui importieren. Verletzungen:\n"
        + "\n".join(f"  {path}: import {mod}" for path, mod in violations)
    )
