"""
Architektur: Segment-Verbotskanten für app.*-Importe (AST).

Regeln: tests/architecture/segment_dependency_rules.py
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_features_source_root import app_features_source_root
from tests.architecture.app_pipelines_source_root import app_pipelines_source_root
from tests.architecture.app_ui_contracts_source_root import app_ui_contracts_source_root
from tests.architecture.arch_guard_config import APP_ROOT
from tests.architecture.segment_dependency_rules import (
    FORBIDDEN_SEGMENT_EDGES,
    IGNORED_SOURCE_SEGMENTS,
    SEGMENT_IMPORT_EXCEPTIONS,
    app_module_from_relpath,
    exception_allows_import,
    is_forbidden_segment_edge,
)


def _source_segment(rel: Path) -> str | None:
    parts = rel.parts
    if len(parts) < 2:
        return None
    return parts[0]


def _target_top_segment(imported_module: str) -> str | None:
    if not imported_module.startswith("app."):
        return None
    rest = imported_module.removeprefix("app.").strip(".")
    if not rest:
        return None
    return rest.split(".", 1)[0]


def _iter_app_import_modules(tree: ast.AST) -> list[str]:
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app."):
                    out.append(name)
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0:
                continue
            mod = node.module
            if mod is None:
                continue
            if mod == "app":
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    out.append(f"app.{alias.name}")
            elif mod.startswith("app."):
                out.append(mod)
    return out


def _iter_segment_scan_targets() -> list[tuple[Path, Path]]:
    """
    (py_path, rel_als_unter_app) — rel so, dass app_module_from_relpath stimmt.

    Host-``app/<segment>/`` plus ausgelagerte Quellen als synthetisches ``features/…``,
    ``ui_contracts/…`` (``app.ui_contracts``) und ``pipelines/…`` (``app.pipelines``).
    """
    out: list[tuple[Path, Path]] = []
    for py_path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        out.append((py_path, py_path.relative_to(APP_ROOT)))
    fr = app_features_source_root()
    for py_path in fr.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        out.append((py_path, Path("features") / py_path.relative_to(fr)))
    uc = app_ui_contracts_source_root()
    for py_path in uc.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        out.append((py_path, Path("ui_contracts") / py_path.relative_to(uc)))
    pl = app_pipelines_source_root()
    for py_path in pl.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        out.append((py_path, Path("pipelines") / py_path.relative_to(pl)))
    return out


def _scan_violations() -> list[str]:
    violations: list[str] = []
    for py_path, rel in _iter_segment_scan_targets():
        rel_posix = rel.as_posix()
        source_seg = _source_segment(rel)
        if source_seg is None or source_seg in IGNORED_SOURCE_SEGMENTS:
            continue
        source_module = app_module_from_relpath(rel_posix)
        if not source_module:
            continue
        try:
            source = py_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=rel_posix)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for imported_mod in _iter_app_import_modules(tree):
            target_seg = _target_top_segment(imported_mod)
            if target_seg is None:
                continue
            if target_seg == source_seg:
                continue
            if not is_forbidden_segment_edge(source_seg, target_seg):
                continue
            if exception_allows_import(source_module, imported_mod):
                continue
            violations.append(
                "\nArchitecture violation:\n\n"
                f"{rel_posix}\n"
                f"(segment: {source_seg})\n"
                "imports\n\n"
                f"    {imported_mod}\n"
                f"(segment: {target_seg})\n\n"
                "Rule violated:\n"
                f"    {source_seg} must not depend on {target_seg}\n\n"
                "See tests/architecture/segment_dependency_rules.py (FORBIDDEN_SEGMENT_EDGES, "
                "SEGMENT_IMPORT_EXCEPTIONS).\n"
            )
    return violations


@pytest.mark.architecture
@pytest.mark.contract
def test_segment_dependency_rules_no_violations():
    violations = _scan_violations()
    assert not violations, "".join(violations[:20]) + (
        f"\n… ({len(violations)} violation(s) total)" if len(violations) > 20 else ""
    )


@pytest.mark.architecture
def test_source_segment_resolution():
    assert _source_segment(Path("gui/foo.py")) == "gui"
    assert _source_segment(Path("main.py")) is None


@pytest.mark.architecture
def test_target_top_segment():
    assert _target_top_segment("app.services.chat_service") == "services"
    assert _target_top_segment("app.gui.x") == "gui"


@pytest.mark.architecture
def test_iter_app_import_modules_simple():
    tree = ast.parse(
        "import os\n"
        "from app.services import chat_service\n"
        "from app.gui.shell import main_window\n"
    )
    mods = _iter_app_import_modules(tree)
    assert any(m == "app.services" or m.startswith("app.services.") for m in mods)
    assert "app.gui.shell" in mods


@pytest.mark.architecture
def test_app_module_from_relpath_init_and_nested():
    assert app_module_from_relpath("gui/__init__.py") == "app.gui"
    assert app_module_from_relpath("core/context/project_context_manager.py") == (
        "app.core.context.project_context_manager"
    )


@pytest.mark.architecture
def test_project_context_manager_exception_matches_real_import():
    src = "app.core.context.project_context_manager"
    assert src in SEGMENT_IMPORT_EXCEPTIONS
    assert exception_allows_import(src, "app.gui.events.project_events")
    assert is_forbidden_segment_edge("core", "gui")
    assert not exception_allows_import(src, "app.gui.shell.main_window")


@pytest.mark.architecture
def test_forbidden_edges_documented_non_empty():
    assert FORBIDDEN_SEGMENT_EDGES


@pytest.mark.architecture
def test_phase2_backbone_must_not_import_gui():
    """Phase 2: dieselbe Schichtregel wie services/core — Backbone ohne PySide."""
    for src in (
        "tools",
        "metrics",
        "debug",
        "persistence",
        "workflows",
        "projects",
        "context",
    ):
        assert is_forbidden_segment_edge(src, "gui"), f"expected ({src}, gui) forbidden"


@pytest.mark.architecture
def test_phase3a_domain_headless_must_not_import_gui():
    """Phase 3A: Chat/LLM-Domäne und CLI ohne direktes app.gui-Paket."""
    for src in ("chat", "chats", "llm", "cli"):
        assert is_forbidden_segment_edge(src, "gui"), f"expected ({src}, gui) forbidden"
