"""
Workspace-Wiring-Regel:

Nutzt ein Workspace-Modul ``wire_panel`` (aus ``app.ui_runtime.panel_wiring``),
dürfen darin keine Presenter-Klassen direkt instanziiert werden
(``SomePresenter(...)``) — Wiring soll über den Helper laufen.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.architecture.app_ui_runtime_source_root import app_ui_runtime_source_root
from tests.architecture.arch_guard_config import APP_ROOT

WORKSPACE_FILES = list((APP_ROOT / "gui").rglob("*workspace*.py"))


def _imports_wire_panel(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in ("app.ui_runtime.panel_wiring", "ui_runtime.panel_wiring"):
                for alias in node.names:
                    if alias.name == "wire_panel":
                        return True
            if mod == "app.ui_runtime":
                for alias in node.names:
                    if alias.name == "wire_panel":
                        return True
    return False


def _instantiates_presenter(tree: ast.Module) -> list[str]:
    """Namen wie ``FooPresenter`` bei direktem Aufruf ``FooPresenter(...)``."""
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name: str | None = None
        if isinstance(f, ast.Name):
            name = f.id
        elif isinstance(f, ast.Attribute):
            name = f.attr
        if name and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*Presenter", name):
            hits.append(name)
    return hits


@pytest.mark.architecture
def test_workspaces_using_wire_panel_do_not_construct_presenters() -> None:
    offenders: list[str] = []
    for path in WORKSPACE_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        if not _imports_wire_panel(tree):
            continue
        bad = _instantiates_presenter(tree)
        if bad:
            rel = path.relative_to(APP_ROOT)
            offenders.append(f"{rel}: {sorted(set(bad))}")
    assert not offenders, (
        "Workspaces that import wire_panel must not call *Presenter(...) directly:\n"
        + "\n".join(offenders)
    )


@pytest.mark.architecture
def test_panel_wiring_module_exists() -> None:
    path = app_ui_runtime_source_root() / "panel_wiring.py"
    assert path.is_file(), "app.ui_runtime.panel_wiring (linux-desktop-chat-ui-runtime) is required for workspace wiring."
