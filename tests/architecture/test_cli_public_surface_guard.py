"""
app.cli: öffentliche Importoberfläche (Welle 5).

- Außerhalb des Paket-Quellbaums: nur ``from app.cli import …`` **oder** Import aus genau
  einer Submodulebene ``app.cli.{context_repro_run,context_replay,…}`` — keine tieferen Pfade.
- Keine Imports von ``_*``-Symbolen aus ``app.cli`` außerhalb des Pakets.

Siehe: docs/architecture/PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_cli_source_root import app_cli_source_root
from tests.architecture.arch_guard_config import (
    APP_ROOT,
    FORBIDDEN_IMPORT_RULES,
    PROJECT_ROOT,
)

_CANONICAL_CLI_MODULES: frozenset[str] = frozenset(
    {
        "app.cli",
        "app.cli.context_repro_run",
        "app.cli.context_replay",
        "app.cli.context_repro_batch",
        "app.cli.context_repro_registry_list",
        "app.cli.context_repro_registry_rebuild",
        "app.cli.context_repro_registry_set_status",
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


def _cli_guard_scan_files() -> list[Path]:
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


def _skip_as_cli_implementation(path: Path) -> bool:
    """True, wenn ``path`` zur Implementierung von ``app.cli`` gehört."""
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] == "cli":
            return True
    except ValueError:
        pass
    try:
        root = app_cli_source_root().resolve()
        path.resolve().relative_to(root)
        return True
    except (ValueError, RuntimeError):
        pass
    return False


def _deep_cli_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _cli_guard_scan_files():
        if _skip_as_cli_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.cli"):
                continue
            if mod not in _CANONICAL_CLI_MODULES:
                bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _should_scan_for_private_cli_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] == "cli":
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-cli":
        if len(rel.parts) >= 5 and rel.parts[1:5] == ("src", "app", "cli"):
            return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_cli_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _cli_guard_scan_files():
        if not _should_scan_for_private_cli_imports(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.cli"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


def _extract_top_imports_from_file(path: Path) -> list[tuple[str, str]]:
    """(source_top, imported_top) für absolute app.*-Importe; Quelle immer ``cli``."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return []
    out: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app."):
                    parts = name.split(".")
                    if len(parts) >= 2:
                        out.append(("cli", parts[1]))
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0 or not node.module:
                continue
            if node.module.startswith("app."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    out.append(("cli", parts[1]))
    return out


def _cli_forbidden_import_violations() -> list[str]:
    """Prüft eingebetteten ``app.cli``-Quellbaum gegen ``FORBIDDEN_IMPORT_RULES``."""
    bad: list[str] = []
    root = app_cli_source_root()
    for py_path in root.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(PROJECT_ROOT) if py_path.is_relative_to(PROJECT_ROOT) else py_path
        for src, dst in _extract_top_imports_from_file(py_path):
            if (src, dst) in FORBIDDEN_IMPORT_RULES:
                bad.append(f"{rel}: app.cli darf app.{dst} nicht importieren (FORBIDDEN_IMPORT_RULES)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_cli_imports_use_canonical_public_modules_only():
    bad = _deep_cli_import_violations()
    assert not bad, (
        "app.cli: nur Paket-Root oder kanonische Submodule außerhalb der "
        "Paket-Implementierung. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_cli_symbols_imported_outside_package():
    bad = _private_cli_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.cli außerhalb "
        "des Pakets. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_cli_package_respects_arch_guard_forbidden_imports():
    bad = _cli_forbidden_import_violations()
    assert not bad, "\n".join(bad)
