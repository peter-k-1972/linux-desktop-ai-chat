"""
Guardrail: Hauptpfad ``_on_agent_selected`` ohne direkten Operations-Read-Service.

Legacy bleibt in ``_apply_ops_detail_legacy``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

WORKSPACE = APP_ROOT / "gui" / "domains" / "operations" / "agent_tasks" / "agent_tasks_workspace.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "AgentTasksWorkspace":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _calls_get_agent_operations_read_service(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == "get_agent_operations_read_service":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "get_agent_operations_read_service":
            return True
    return False


@pytest.mark.architecture
def test_workspace_on_agent_selected_avoids_direct_operations_read_service() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_agent_selected")
    assert fn is not None
    assert not _calls_get_agent_operations_read_service(fn), (
        "_on_agent_selected must not call get_agent_operations_read_service "
        "(use Presenter/Port/Adapter; legacy only in _apply_ops_detail_legacy)."
    )


@pytest.mark.architecture
def test_workspace_legacy_detail_still_uses_operations_read_service() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_apply_ops_detail_legacy")
    assert fn is not None
    assert _calls_get_agent_operations_read_service(fn), (
        "_apply_ops_detail_legacy should call get_agent_operations_read_service for fallback."
    )


@pytest.mark.architecture
def test_refresh_agents_avoids_direct_operations_read_service() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_refresh_agents")
    assert fn is not None
    assert not _calls_get_agent_operations_read_service(fn), (
        "_refresh_agents must not call get_agent_operations_read_service (summary read via Presenter/Adapter)."
    )
