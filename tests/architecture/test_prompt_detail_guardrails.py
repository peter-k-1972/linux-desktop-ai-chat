"""
Guardrail: ``PromptListPanel._on_prompt_selected`` ohne direkten ``get_prompt_service``.

Legacy bleibt in ``_load_prompts_legacy`` / ``_add_prompt_item`` / ``_on_delete_prompt``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "prompt_studio" / "panels" / "prompt_list_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "PromptListPanel":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _calls_get_prompt_service(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == "get_prompt_service":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "get_prompt_service":
            return True
    return False


@pytest.mark.architecture
def test_prompt_list_panel_on_prompt_selected_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_prompt_selected")
    assert fn is not None
    assert not _calls_get_prompt_service(fn), (
        "_on_prompt_selected must not call get_prompt_service (use Presenter/Port/Adapter)."
    )
