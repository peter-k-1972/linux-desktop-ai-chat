"""
app.runtime / app.extensions: öffentliche Importoberfläche (Welle 10).

- Außerhalb des Paket-Quellbaums: nur kanonische Modulpfade.
- Keine Imports von ``_*``-Symbolen aus diesen Paketen außerhalb der Implementierung.

Siehe: docs/architecture/PACKAGE_RUNTIME_PHYSICAL_SPLIT.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_runtime_source_root import (
    app_extensions_source_root,
    app_runtime_source_root,
)
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_RUNTIME_MODULES: frozenset[str] = frozenset(
    {
        "app.runtime",
        "app.runtime.lifecycle",
        "app.runtime.model_invocation",
        "app.extensions",
    }
)

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


def _runtime_guard_scan_files() -> list[Path]:
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


def _skip_as_runtime_implementation(path: Path) -> bool:
    for root_fn in (app_runtime_source_root, app_extensions_source_root):
        try:
            root = root_fn().resolve()
        except RuntimeError:
            continue
        try:
            path.resolve().relative_to(root)
            return True
        except ValueError:
            continue
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] in ("runtime", "extensions"):
            return True
    except ValueError:
        pass
    return False


def _deep_runtime_import_violations() -> list[str]:
    bad: list[str] = []
    prefixes = ("app.runtime.", "app.extensions.")
    for path in _runtime_guard_scan_files():
        if _skip_as_runtime_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                mod = node.module
                if not mod:
                    continue
                if mod.startswith("app.runtime.") or mod.startswith("app.extensions."):
                    if mod not in _CANONICAL_RUNTIME_MODULES:
                        bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
                elif mod in ("app.runtime", "app.extensions"):
                    pass  # root imports OK
    return bad


def _should_scan_for_private_runtime_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] in ("runtime", "extensions"):
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-runtime":
        if len(rel.parts) >= 4 and rel.parts[1] == "src" and rel.parts[2] == "app":
            if rel.parts[3] in ("runtime", "extensions"):
                return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_runtime_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    prefixes = ("app.runtime.", "app.extensions.")
    for path in _runtime_guard_scan_files():
        if not _should_scan_for_private_runtime_imports(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith(prefixes):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_runtime_imports_use_canonical_public_modules_only():
    bad = _deep_runtime_import_violations()
    assert not bad, (
        "app.runtime / app.extensions: nur kanonische Submodule außerhalb "
        "der Paket-Implementierung. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_runtime_symbols_imported_outside_package():
    bad = _private_runtime_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.runtime/app.extensions "
        "außerhalb der Pakete. Verstöße:\n" + "\n".join(bad)
    )
