"""
Guardrail: ``RolloutsPanel.refresh()`` ruft ``get_deployment_operations_service`` nicht auf.

Erlaubt in ``_refresh_legacy`` / ``_reload_filter_combos_legacy`` und ``_on_record_legacy`` (Batch 7).
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "deployment" / "panels" / "rollouts_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "RolloutsPanel":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return item
    return None


def _calls_get_deployment_service(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == "get_deployment_operations_service":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "get_deployment_operations_service":
            return True
    return False


@pytest.mark.architecture
def test_rollouts_panel_refresh_avoids_direct_deployment_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "refresh")
    assert fn is not None
    assert not _calls_get_deployment_service(fn), (
        "refresh() must not call get_deployment_operations_service directly "
        "(use Presenter/Port or _refresh_legacy)."
    )


@pytest.mark.architecture
def test_rollouts_panel_on_record_avoids_direct_deployment_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_record")
    assert fn is not None
    assert not _calls_get_deployment_service(fn), (
        "_on_record must not call get_deployment_operations_service (Batch 7: use Presenter/Port; legacy in _on_record_legacy)."
    )


@pytest.mark.architecture
def test_rollouts_panel_on_record_legacy_uses_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_record_legacy")
    assert fn is not None
    assert _calls_get_deployment_service(fn), "_on_record_legacy should call the deployment service."
