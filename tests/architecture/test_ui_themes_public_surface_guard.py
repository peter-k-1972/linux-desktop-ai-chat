"""
app.ui_themes: öffentliche Importoberfläche (Welle 7).

- Außerhalb des Paket-Quellbaums: nur ``import app.ui_themes`` bzw. ``from app.ui_themes import …``
  — keine tieferen ``app.ui_themes.*``-Modulpfade (keine Python-Submodule unter builtins).

Siehe: docs/architecture/PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_ui_themes_source_root import app_ui_themes_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_MODULES: frozenset[str] = frozenset({"app.ui_themes"})

_SKIP_DIR_PARTS = frozenset({
    ".venv",
    ".venv-commit2",
    ".venv-commit2-ui",
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
})


def _iter_py_files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and not _SKIP_DIR_PARTS.intersection(p.parts)
    ]


def _guard_scan_files() -> list[Path]:
    roots = [
        APP_ROOT,
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "tools",
        PROJECT_ROOT / "examples",
    ]
    scripts = PROJECT_ROOT / "scripts"
    if scripts.is_dir():
        roots.append(scripts)
    out: list[Path] = []
    for r in roots:
        if r.is_dir():
            out.extend(_iter_py_files(r))
    return out


def _skip_as_implementation(path: Path) -> bool:
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] == "ui_themes":
            return True
    except ValueError:
        pass
    try:
        root = app_ui_themes_source_root().resolve()
        path.resolve().relative_to(root)
        return True
    except (ValueError, RuntimeError):
        pass
    return False


def _deep_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _guard_scan_files():
        if _skip_as_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if mod.startswith("app.ui_themes.") and mod not in _CANONICAL_MODULES:
                        bad.append(f"{path}: import {mod}")
            elif isinstance(node, ast.ImportFrom):
                if node.level != 0 or node.module is None:
                    continue
                mod = node.module
                if mod.startswith("app.ui_themes.") and mod not in _CANONICAL_MODULES:
                    bad.append(f"{path}: from {mod} import …")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_themes_imports_use_package_root_only():
    bad = _deep_import_violations()
    assert not bad, (
        "app.ui_themes: außerhalb des Pakets nur Import des Paket-Roots — "
        f"keine Submodule: {bad}"
    )
