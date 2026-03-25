"""
app.providers: öffentliche Importoberfläche (Welle 4). Cut-Ready / DoR:
docs/architecture/PACKAGE_PROVIDERS_CUT_READY.md

Commit 2: Ausschluss der **Implementierung** nutzt ``app_providers_source_root()`` (installierte
Quelle) sowie das historische Host-Muster ``app/providers/…`` (falls lokal noch vorhanden).

- Außerhalb des Paket-Quellbaums: nur ``from app.providers import …`` **oder** Import aus genau
  einer Submodulebene ``app.providers.{base_provider,ollama_client,cloud_ollama_provider,
  local_ollama_provider,orchestrator_provider_factory}`` — keine tieferen Pfade.
- Keine Imports von ``_*``-Symbolen aus ``app.providers`` außerhalb des Pakets.

Siehe: docs/architecture/PACKAGE_PROVIDERS_SPLIT_READY.md,
docs/architecture/PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_providers_source_root import app_providers_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_PROVIDER_MODULES: frozenset[str] = frozenset(
    {
        "app.providers",
        "app.providers.base_provider",
        "app.providers.ollama_client",
        "app.providers.cloud_ollama_provider",
        "app.providers.local_ollama_provider",
        "app.providers.orchestrator_provider_factory",
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


def _providers_guard_scan_files() -> list[Path]:
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


def _skip_as_providers_implementation(path: Path) -> bool:
    """True, wenn ``path`` zur Implementierung von ``app.providers`` gehört."""
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] == "providers":
            return True
    except ValueError:
        pass
    try:
        root = app_providers_source_root().resolve()
        path.resolve().relative_to(root)
        return True
    except (ValueError, RuntimeError):
        pass
    return False


def _deep_providers_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _providers_guard_scan_files():
        if _skip_as_providers_implementation(path):
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
            if not mod or not mod.startswith("app.providers"):
                continue
            if mod not in _CANONICAL_PROVIDER_MODULES:
                bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _should_scan_for_private_providers_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] == "providers":
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-providers":
        if len(rel.parts) >= 5 and rel.parts[1:5] == ("src", "app", "providers"):
            return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_providers_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _providers_guard_scan_files():
        if not _should_scan_for_private_providers_imports(path):
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
            if not mod or not mod.startswith("app.providers"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_providers_imports_use_canonical_public_modules_only():
    bad = _deep_providers_import_violations()
    assert not bad, (
        "app.providers: nur Paket-Root oder app.providers.{base_provider,ollama_client,"
        "cloud_ollama_provider,local_ollama_provider,orchestrator_provider_factory} "
        "außerhalb der Paket-Implementierung. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_providers_symbols_imported_outside_package():
    bad = _private_providers_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.providers außerhalb "
        "des Pakets. Verstöße:\n" + "\n".join(bad)
    )
