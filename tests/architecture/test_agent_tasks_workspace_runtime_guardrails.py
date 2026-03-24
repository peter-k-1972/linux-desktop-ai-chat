"""
Guardrail: AgentTasksWorkspace — Hauptpfad ``_run_task`` ohne direkten ``start_agent_task``.

Legacy bleibt in ``_run_task_legacy``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

WORKSPACE = APP_ROOT / "gui" / "domains" / "operations" / "agent_tasks" / "agent_tasks_workspace.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "AgentTasksWorkspace":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return item
    return None


def _calls_start_agent_task_on_get_agent_service(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Attribute) and f.attr == "start_agent_task":
            return True
    return False


@pytest.mark.architecture
def test_run_task_avoids_direct_start_agent_task() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_run_task")
    assert fn is not None
    assert not _calls_start_agent_task_on_get_agent_service(fn), (
        "_run_task must not call .start_agent_task directly (use Presenter/Port/Adapter; legacy in _run_task_legacy)."
    )


@pytest.mark.architecture
def test_run_task_legacy_still_calls_start_agent_task() -> None:
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_run_task_legacy")
    assert fn is not None
    assert _calls_start_agent_task_on_get_agent_service(fn), (
        "_run_task_legacy should call start_agent_task for fallback."
    )
