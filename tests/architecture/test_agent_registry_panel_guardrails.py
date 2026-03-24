"""
Guardrail: ``AgentRegistryPanel.refresh()`` ruft ``get_agent_service`` nicht auf.

Erlaubt in ``_refresh_legacy``; ``get_agent_operations_read_service`` nur im Adapter (Slice 1).
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "agent_tasks" / "panels" / "agent_registry_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "AgentRegistryPanel":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _calls_get_agent_service(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == "get_agent_service":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "get_agent_service":
            return True
    return False


@pytest.mark.architecture
def test_registry_panel_refresh_avoids_direct_agent_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "refresh")
    assert fn is not None
    assert not _calls_get_agent_service(fn), (
        "refresh() must not call get_agent_service directly (use Presenter/Port or _refresh_legacy)."
    )


@pytest.mark.architecture
def test_registry_legacy_still_uses_agent_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_refresh_legacy")
    assert fn is not None
    assert _calls_get_agent_service(fn), "_refresh_legacy should still call get_agent_service."
