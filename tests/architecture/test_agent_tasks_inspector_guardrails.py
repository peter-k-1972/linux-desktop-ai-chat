"""
Guardrail: ``_refresh_inspector`` ohne direkten ``get_agent_operations_read_service``.

Read läuft über Presenter → Port → Adapter (Slice 3).
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
def test_workspace_refresh_inspector_avoids_direct_operations_read_service() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_refresh_inspector")
    assert fn is not None
    assert not _calls_get_agent_operations_read_service(fn), (
        "_refresh_inspector must not call get_agent_operations_read_service "
        "(Inspector read via Presenter/Port/Adapter)."
    )
