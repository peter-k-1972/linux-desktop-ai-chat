"""
app.ui_contracts: keine Imports von ``_*``-Symbolen außerhalb des Pakets.

Im Gegensatz zu ``app.features`` bleiben ``from app.ui_contracts.workspaces.<mod> import …``
absichtlich erlaubt (zweite öffentliche API-Ebene). Dieser Guard ergänzt nur die
Unterstrich-Konvention für echte Private-API-Versuche.

Der Walk ist **nur** ``PROJECT_ROOT`` (Host-Repo); der Paketquellbaum liegt installiert
(``find_spec``), nicht unter ``app/ui_contracts/`` im Monorepo. Die Ausschlussregel für
Pfade ``app/ui_contracts/…`` bleibt für Klarheit / hypothetische lokale Trees.

Siehe: docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import PROJECT_ROOT


def _iter_py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _should_scan_for_private_ui_contracts_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] == "ui_contracts":
            return False
        return True
    if rel.parts[0] == "tests":
        return True
    if rel.parts[0] in ("examples", "tools"):
        return True
    return False


def _private_ui_contracts_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _iter_py_files(PROJECT_ROOT):
        if not _should_scan_for_private_ui_contracts_imports(path):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.ui_contracts"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_ui_contracts_symbols_imported_outside_package():
    bad = _private_ui_contracts_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.ui_contracts außerhalb "
        "des Pakets (Host-/Test-/Tool-Code im Repo-Tree). Verstöße:\n" + "\n".join(bad)
    )
