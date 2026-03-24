"""
Guardrail: ``PromptVersionPanel.set_prompt`` / ``refresh`` Hauptpfad ohne ``get_prompt_service``.

Legacy bleibt ``_load_versions_from_service``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "prompt_studio" / "panels" / "prompt_version_panel.py"


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "PromptVersionPanel":
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
def test_prompt_version_set_prompt_avoids_service_on_port_branch() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "set_prompt")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_version_refresh_avoids_service_when_port_path() -> None:
    """refresh() delegiert zu Presenter oder Legacy — kein direkter Aufruf in refresh selbst."""
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "refresh")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_version_apply_state_avoids_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "apply_prompt_version_panel_state")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_version_on_version_clicked_avoids_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_version_clicked")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_version_add_version_item_avoids_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_add_version_item")
    assert fn is not None
    assert not _calls_get_prompt_service(fn)


@pytest.mark.architecture
def test_prompt_version_load_versions_legacy_uses_service() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_load_versions_from_service")
    assert fn is not None
    assert _calls_get_prompt_service(fn)
