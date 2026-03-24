"""
Guardrail: ``refresh`` und ``_on_sel`` des ReleasesPanel ohne direkten Deployment-Service.

Mutationen (Batch 4): ``_on_new``, ``_on_edit``, ``_on_archive`` ebenfalls ohne direkten Service.

Erlaubt nur in Legacy-Helfern (``_refresh_legacy``, ``_on_sel_legacy``, ``_on_*_legacy``).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "deployment" / "panels" / "releases_panel.py"

_BANNED_CALLEES = (
    "get_deployment_operations_service",
    "get_project_service",
    "get_infrastructure",
)


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ReleasesPanel":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _calls_name(func: ast.FunctionDef, callee: str) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == callee:
            return True
        if isinstance(f, ast.Attribute) and f.attr == callee:
            return True
    return False


@pytest.mark.architecture
@pytest.mark.parametrize(
    "method_name",
    ("refresh", "_on_sel", "_on_new", "_on_edit", "_on_archive"),
)
@pytest.mark.parametrize("callee", _BANNED_CALLEES)
def test_releases_panel_main_methods_avoid_banned_calls(method_name: str, callee: str) -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, method_name)
    assert fn is not None
    assert not _calls_name(fn, callee), (
        f"{method_name}() must not call {callee} directly "
        "(use Presenter/Port/Adapter; legacy only in *_legacy helpers)."
    )
