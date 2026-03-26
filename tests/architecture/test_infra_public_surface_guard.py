"""
app.debug / app.metrics / app.tools: öffentliche Importoberfläche (Welle 9).

- Außerhalb des Paket-Quellbaums: nur kanonische Modulpfade (ein Submodul-Level
  unter ``app.debug``, ``app.metrics``, ``app.tools``).
- Keine Imports von ``_*``-Symbolen aus diesen Paketen außerhalb der Implementierung.

Siehe: docs/architecture/PACKAGE_INFRA_PHYSICAL_SPLIT.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_infra_source_root import app_infra_segment_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_INFRA_MODULES: frozenset[str] = frozenset(
    {
        "app.debug",
        "app.debug.agent_event",
        "app.debug.debug_store",
        "app.debug.emitter",
        "app.debug.event_bus",
        "app.debug.gui_log_buffer",
        "app.debug.qa_artifact_loader",
        "app.debug.qa_cockpit_panel",
        "app.metrics",
        "app.metrics.agent_metrics",
        "app.metrics.metrics_collector",
        "app.metrics.metrics_service",
        "app.metrics.metrics_store",
        "app.tools",
        "app.tools.filesystem",
        "app.tools.web_search",
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


def _infra_guard_scan_files() -> list[Path]:
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


def _skip_as_infra_implementation(path: Path) -> bool:
    for seg in ("debug", "metrics", "tools"):
        try:
            root = app_infra_segment_source_root(seg).resolve()
        except RuntimeError:
            continue
        try:
            path.resolve().relative_to(root)
            return True
        except ValueError:
            continue
    try:
        rel = path.relative_to(APP_ROOT)
        if len(rel.parts) > 0 and rel.parts[0] in ("debug", "metrics", "tools"):
            return True
    except ValueError:
        pass
    return False


def _deep_infra_import_violations() -> list[str]:
    bad: list[str] = []
    prefixes = ("app.debug.", "app.metrics.", "app.tools.")
    for path in _infra_guard_scan_files():
        if _skip_as_infra_implementation(path):
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
                if not mod or not mod.startswith(prefixes):
                    continue
                if mod not in _CANONICAL_INFRA_MODULES:
                    bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _should_scan_for_private_infra_imports(path: Path) -> bool:
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    if rel.parts[0] == "app":
        if len(rel.parts) > 1 and rel.parts[1] in ("debug", "metrics", "tools"):
            return False
        return True
    if rel.parts[0] == "linux-desktop-chat-infra":
        if len(rel.parts) >= 4 and rel.parts[1] == "src" and rel.parts[2] == "app":
            if rel.parts[3] in ("debug", "metrics", "tools"):
                return False
        return True
    if rel.parts[0] in ("tests", "tools", "examples", "scripts"):
        return True
    return False


def _private_infra_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    prefixes = ("app.debug.", "app.metrics.", "app.tools.")
    for path in _infra_guard_scan_files():
        if not _should_scan_for_private_infra_imports(path):
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
def test_infra_imports_use_canonical_public_modules_only():
    bad = _deep_infra_import_violations()
    assert not bad, (
        "app.debug / app.metrics / app.tools: nur kanonische Submodule außerhalb "
        "der Paket-Implementierung. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_infra_symbols_imported_outside_package():
    bad = _private_infra_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.debug/metrics/tools "
        "außerhalb der Pakete. Verstöße:\n" + "\n".join(bad)
    )
