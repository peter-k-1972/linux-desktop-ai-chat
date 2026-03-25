"""
app.pipelines: öffentliche Importoberfläche (Welle 3). Cut-Ready / DoR:
docs/architecture/PACKAGE_PIPELINES_CUT_READY.md

Commit 4: Ausschluss der **Implementierung** nutzt ``app_pipelines_source_root()`` (installierte
Quelle) sowie das historische Host-Muster ``app/pipelines/…`` (falls lokal noch vorhanden).
Der Walk bleibt ``app/``, ``tests/``, ``tools/``, ``examples/``, ``scripts/`` — keine
Voll-Repo-Pfade durch ``linux-desktop-chat-pipelines/``.

- Außerhalb des Paket-Quellbaums: nur ``from app.pipelines import …`` **oder** Import aus genau
  einer Submodulebene ``app.pipelines.{models,engine,services,executors,registry}`` — keine tieferen
  Pfade (z. B. kein ``app.pipelines.engine.engine``).
- Keine Imports von ``_*``-Symbolen aus ``app.pipelines`` außerhalb des Pakets.

Siehe: docs/architecture/PACKAGE_PIPELINES_SPLIT_READY.md,
``docs/architecture/PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_pipelines_source_root import app_pipelines_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_PIPELINES_MODULES: frozenset[str] = frozenset(
    {
        "app.pipelines",
        "app.pipelines.models",
        "app.pipelines.engine",
        "app.pipelines.services",
        "app.pipelines.executors",
        "app.pipelines.registry",
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


def _pipelines_guard_scan_files() -> list[Path]:
    """Nur Produkt- und Werkzeugbäume — kein Voll-Repo-Walk (Performance)."""
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


def _skip_as_pipelines_implementation(path: Path) -> bool:
    """True, wenn ``path`` zur Implementierung von ``app.pipelines`` gehört (nicht Consumer-Check)."""
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] == "pipelines":
            return True
    except ValueError:
        pass
    try:
        root = app_pipelines_source_root().resolve()
        path.resolve().relative_to(root)
        return True
    except (ValueError, RuntimeError):
        pass
    return False


def _deep_pipelines_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _pipelines_guard_scan_files():
        if _skip_as_pipelines_implementation(path):
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
            if not mod or not mod.startswith("app.pipelines"):
                continue
            if mod not in _CANONICAL_PIPELINES_MODULES:
                bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _should_scan_for_private_pipelines_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] == "pipelines":
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-pipelines":
        if len(rel.parts) >= 5 and rel.parts[1:5] == ("src", "app", "pipelines"):
            return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_pipelines_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _pipelines_guard_scan_files():
        if not _should_scan_for_private_pipelines_imports(path):
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
            if not mod or not mod.startswith("app.pipelines"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
def test_pipelines_imports_use_canonical_public_modules_only():
    bad = _deep_pipelines_import_violations()
    assert not bad, (
        "app.pipelines: nur Paket-Root oder app.pipelines.{models,engine,services,"
        "executors,registry} außerhalb der Paket-Implementierung. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
def test_no_private_pipelines_symbols_imported_outside_package():
    bad = _private_pipelines_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.pipelines außerhalb "
        "des Pakets. Verstöße:\n" + "\n".join(bad)
    )
