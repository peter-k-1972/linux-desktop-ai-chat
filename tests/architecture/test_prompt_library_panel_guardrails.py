"""
Guardrail: ``PromptLibraryPanel.refresh()`` ohne direkten ``get_prompt_service``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "prompt_studio" / "panels" / "library_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "PromptLibraryPanel":
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
def test_prompt_library_refresh_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "refresh")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_library_apply_state_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "apply_prompt_library_state")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_library_on_delete_prompt_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_delete_prompt")
    assert fn is not None
    assert not _calls_get_prompt_service(fn), (
        "_on_delete_prompt must not call get_prompt_service (Batch 7: Presenter/Port; legacy in _on_delete_prompt_legacy)."
    )


@pytest.mark.architecture
def test_prompt_library_add_prompt_item_avoids_direct_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_add_prompt_item")
    assert fn is not None
    assert not _calls_get_prompt_service(fn), (
        "_add_prompt_item must not call get_prompt_service (Batch 8: legacy only in _version_count_from_service_legacy)."
    )


@pytest.mark.architecture
def test_prompt_library_version_count_legacy_uses_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_version_count_from_service_legacy")
    assert fn is not None
    assert _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_library_on_delete_legacy_uses_prompt_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_delete_prompt_legacy")
    assert fn is not None
    assert _calls_get_prompt_service(fn)
