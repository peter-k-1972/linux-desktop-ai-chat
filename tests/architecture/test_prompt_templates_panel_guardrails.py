"""
Guardrail: ``PromptTemplatesPanel.refresh`` / ``apply_prompt_templates_state`` ohne ``get_prompt_service``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "prompt_studio" / "panels" / "prompt_templates_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "PromptTemplatesPanel":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return item
    return None


def _calls_get_prompt_service(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
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
def test_prompt_templates_refresh_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "refresh")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_templates_apply_state_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "apply_prompt_templates_state")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
@pytest.mark.parametrize(
    "method",
    ["_on_create", "_on_edit", "_on_copy_to_prompt", "_on_delete"],
)
def test_prompt_templates_mutation_main_path_avoids_prompt_service(method: str) -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, method)
    assert fn is not None
    assert not _calls_get_prompt_service(fn), (
        f"PromptTemplatesPanel.{method} must not call get_prompt_service on main path (Batch 7: *_legacy)."
    )


@pytest.mark.architecture
@pytest.mark.parametrize(
    "method",
    ["_on_create_legacy", "_on_edit_legacy", "_on_copy_to_prompt_legacy", "_on_delete_legacy"],
)
def test_prompt_templates_legacy_mutations_use_prompt_service(method: str) -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, method)
    assert fn is not None
    assert _calls_get_prompt_service(fn), f"{method} should retain get_prompt_service for legacy."
