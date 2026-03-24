"""
Prompt Studio: ``get_*_service`` nur in explizit erlaubten Legacy-Methoden (AST).

Neue direkte Service-Aufrufe in anderen Methoden brechen den Guard.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

BASE = APP_ROOT / "gui" / "domains" / "operations" / "prompt_studio"

_SERVICE_ATTRS = frozenset({"get_prompt_service", "get_model_service", "get_chat_service"})


def _class_methods(tree: ast.Module, class_name: str) -> list[ast.FunctionDef]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [item for item in node.body if isinstance(item, ast.FunctionDef)]
    return []


def _function_calls_service(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id in _SERVICE_ATTRS:
            return True
        if isinstance(f, ast.Attribute) and f.attr in _SERVICE_ATTRS:
            return True
    return False


def _assert_bounded(path: Path, class_name: str, allowed_with_service: frozenset[str]) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for fn in _class_methods(tree, class_name):
        if fn.name in allowed_with_service:
            continue
        if "_legacy" in fn.name:
            continue
        if _function_calls_service(fn):
            pytest.fail(
                f"{path.name}::{class_name}.{fn.name} must not call get_*_service "
                f"(or add to allowed_with_service if intentional legacy).",
            )


@pytest.mark.architecture
@pytest.mark.parametrize(
    ("rel_path", "class_name", "allowed"),
    [
        (
            "panels/prompt_editor_panel.py",
            "PromptEditorPanel",
            frozenset({"_on_save_legacy"}),
        ),
        (
            "panels/editor_panel.py",
            "PromptEditorPanel",
            frozenset({"_on_save_legacy"}),
        ),
        (
            "panels/prompt_version_panel.py",
            "PromptVersionPanel",
            frozenset({"_load_versions_from_service"}),
        ),
        (
            "panels/library_panel.py",
            "PromptLibraryPanel",
            frozenset({"_load_prompts_legacy", "_on_delete_prompt", "_add_prompt_item"}),
        ),
        (
            "panels/prompt_templates_panel.py",
            "PromptTemplatesPanel",
            frozenset(
                {
                    "_load_templates_legacy",
                    "_on_create",
                    "_on_edit",
                    "_on_copy_to_prompt",
                    "_on_delete",
                },
            ),
        ),
        (
            "prompt_studio_workspace.py",
            "PromptStudioWorkspace",
            frozenset({"_on_new_prompt_legacy", "_open_with_context_legacy"}),
        ),
    ],
)
def test_prompt_studio_service_calls_bounded(
    rel_path: str,
    class_name: str,
    allowed: frozenset[str],
) -> None:
    _assert_bounded(BASE / rel_path, class_name, allowed)
