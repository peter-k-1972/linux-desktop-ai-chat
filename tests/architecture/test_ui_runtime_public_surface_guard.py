"""
app.ui_runtime: öffentliche Importoberfläche (Welle 8).

Außerhalb des Paket-Quellbaums: nur Imports, deren Modulpfad in
``_CANONICAL_UI_RUNTIME_MODULES`` liegt — keine tieferen/unbekannten ``app.ui_runtime.…``-Pfade.
Keine ``_*``-Symbol-Imports aus ``app.ui_runtime`` außerhalb des Pakets.

Siehe: docs/architecture/PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_ui_runtime_source_root import app_ui_runtime_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_UI_RUNTIME_MODULES: frozenset[str] = frozenset(
    {
        "app.ui_runtime",
        "app.ui_runtime.base_runtime",
        "app.ui_runtime.command_dispatcher",
        "app.ui_runtime.manifest_models",
        "app.ui_runtime.panel_wiring",
        "app.ui_runtime.theme_loader",
        "app.ui_runtime.theme_registry",
        "app.ui_runtime.widgets",
        "app.ui_runtime.widgets.widgets_runtime",
        "app.ui_runtime.qml",
        "app.ui_runtime.qml.qml_runtime",
        "app.ui_runtime.qml.shell_bridge_facade",
        "app.ui_runtime.qml.shell_navigation_state",
        "app.ui_runtime.qml.shell_route_catalog",
        "app.ui_runtime.qml.domain_nav_model",
        "app.ui_runtime.qml.chat",
        "app.ui_runtime.qml.chat.chat_models",
        "app.ui_runtime.qml.chat.chat_qml_viewmodel",
        "app.ui_runtime.qml.presenters",
        "app.ui_runtime.qml.presenters.shell_presenter",
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


def _skip_as_ui_runtime_implementation(path: Path) -> bool:
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] == "ui_runtime":
            return True
    except ValueError:
        pass
    try:
        root = app_ui_runtime_source_root().resolve()
        path.resolve().relative_to(root)
        return True
    except (ValueError, RuntimeError):
        pass
    return False


def _deep_ui_runtime_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _guard_scan_files():
        if _skip_as_ui_runtime_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if not mod.startswith("app.ui_runtime"):
                        continue
                    if mod not in _CANONICAL_UI_RUNTIME_MODULES:
                        bad.append(f"{rel}: import {mod} (nicht kanonische Public-Surface)")
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                mod = node.module
                if not mod or not mod.startswith("app.ui_runtime"):
                    continue
                if mod not in _CANONICAL_UI_RUNTIME_MODULES:
                    bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _should_scan_for_private_ui_runtime_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] == "ui_runtime":
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-ui-runtime":
        if len(rel.parts) >= 5 and rel.parts[1:5] == ("src", "app", "ui_runtime"):
            return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_ui_runtime_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _guard_scan_files():
        if not _should_scan_for_private_ui_runtime_imports(path):
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
            if not mod or not mod.startswith("app.ui_runtime"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_runtime_imports_use_canonical_public_modules_only():
    bad = _deep_ui_runtime_import_violations()
    assert not bad, (
        "app.ui_runtime: nur kanonische Submodule außerhalb der Paket-Implementierung. "
        "Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_ui_runtime_symbols_imported_outside_package():
    bad = _private_ui_runtime_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.ui_runtime außerhalb "
        "des Pakets. Verstöße:\n" + "\n".join(bad)
    )
