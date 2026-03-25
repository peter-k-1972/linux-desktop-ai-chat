"""
app.features: öffentliche Importoberfläche für den späteren Repo-Split.

- Host-Produktcode unter ``app/`` (ohne lokale ``features``-Quelle): nur
  ``from app.features import …``, keine tieferen ``app.features.<submodul>``-Importe.
- tools/ci: zusätzlich erlaubt ``release_matrix`` und ``dependency_packaging``.
- Keine Imports von ``_*``-Symbolen aus app.features außerhalb der ``app.features``-Quelle
  (Distribution) und ``tests/unit/features/`` (Discovery-Interna-Tests).

Siehe: docs/architecture/PACKAGE_FEATURES_CUT_READY.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

# CI-Einstiegspunkte — bleiben stabile Submodule bis ggf. Root-Re-Export.
_CI_ALLOWED_FEATURE_SUBMODULES: frozenset[str] = frozenset(
    {
        "app.features.release_matrix",
        "app.features.dependency_packaging",
    }
)


def _iter_py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _under_host_app_features_dir(path: Path) -> bool:
    """True nur noch, falls jemals wieder ``app/features`` unter dem Host-APP_ROOT liegt."""
    try:
        rel = path.relative_to(APP_ROOT)
    except ValueError:
        return False
    return len(rel.parts) > 0 and rel.parts[0] == "features"


def _is_tools_ci_file(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    return len(rel.parts) >= 2 and rel.parts[0] == "tools" and rel.parts[1] == "ci"


def _submodule_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _iter_py_files(APP_ROOT):
        if _under_host_app_features_dir(path):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.features"):
                continue
            if mod == "app.features":
                continue
            if _is_tools_ci_file(path) and mod in _CI_ALLOWED_FEATURE_SUBMODULES:
                continue
            bad.append(f"{path.relative_to(PROJECT_ROOT)}: from {mod} import …")
    return bad


def _should_scan_for_private_feature_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        # Legacy: Host-Tree app/features/ (heute leer); ausgelagerte Quelle unter linux-desktop-chat-features/
        return not (len(rel.parts) > 1 and rel.parts[1] == "features")
    if rel.parts[0] == "tests":
        if len(rel.parts) >= 3 and rel.parts[1] == "unit" and rel.parts[2] == "features":
            return False
        return True
    if rel.parts[0] in ("examples", "tools"):
        return True
    return False


def _private_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _iter_py_files(PROJECT_ROOT):
        if not _should_scan_for_private_feature_imports(path):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.features"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_app_code_does_not_import_features_submodules_directly():
    bad = _submodule_import_violations()
    assert not bad, (
        "Produktcode unter app/ soll app.features nur über Paket-Root importieren "
        "(docs/architecture/PACKAGE_FEATURES_CUT_READY.md). Verstöße:\n"
        + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_feature_symbols_imported_outside_features_and_unit_tests():
    bad = _private_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend Unterstrich-Symbolen aus app.features außerhalb "
        "der app.features-Quelle (Distribution) und tests/unit/features/. Verstöße:\n"
        + "\n".join(bad)
    )
