"""
Guardrail: PromptTestLab — Hauptpfad-Lesen ohne get_prompt_service / get_model_service;
Hauptpfad-Run ohne get_chat_service (Batch 6).

Erlaubt: ``_*_legacy`` explizit; Chat nur in ``_run_prompt_legacy``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = (
    APP_ROOT
    / "gui"
    / "domains"
    / "operations"
    / "prompt_studio"
    / "panels"
    / "prompt_test_lab.py"
)

_FORBIDDEN_READ = frozenset({"get_prompt_service", "get_model_service"})
_FORBIDDEN_CHAT = frozenset({"get_chat_service"})


def _class_methods(tree: ast.Module, class_name: str) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [
                item
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
    return []


def _function_calls_name(func: ast.FunctionDef | ast.AsyncFunctionDef, names: frozenset[str]) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id in names:
            return True
        if isinstance(f, ast.Attribute) and f.attr in names:
            return True
    return False


@pytest.mark.architecture
@pytest.mark.parametrize(
    "method",
    [
        "_load_prompts_async",
        "_load_models_async",
        "_on_prompt_changed",
    ],
)
def test_migrated_read_methods_avoid_prompt_and_model_service(method: str) -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fns = {fn.name: fn for fn in _class_methods(tree, "PromptTestLab")}
    fn = fns[method]
    assert not _function_calls_name(fn, _FORBIDDEN_READ), (
        f"PromptTestLab.{method} must not call get_prompt_service/get_model_service "
        "(use Presenter/Port/Adapter; legacy only in *_legacy)."
    )


@pytest.mark.architecture
@pytest.mark.parametrize(
    "method",
    [
        "_on_run",
        "_run_via_presenter",
    ],
)
def test_migrated_run_path_avoids_chat_service(method: str) -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fns = {fn.name: fn for fn in _class_methods(tree, "PromptTestLab")}
    fn = fns[method]
    assert not _function_calls_name(fn, _FORBIDDEN_CHAT), (
        f"PromptTestLab.{method} must not call get_chat_service "
        "(use Presenter/Port/Adapter; legacy only in _run_prompt_legacy)."
    )


@pytest.mark.architecture
def test_legacy_loaders_still_touch_services() -> None:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    fns = {fn.name: fn for fn in _class_methods(tree, "PromptTestLab")}
    assert _function_calls_name(fns["_load_prompts_async_legacy"], frozenset({"get_prompt_service"}))
    assert _function_calls_name(fns["_load_models_async_legacy"], frozenset({"get_model_service"}))
    assert _function_calls_name(fns["_on_prompt_changed_legacy"], frozenset({"get_prompt_service"}))
    assert _function_calls_name(fns["_run_prompt_legacy"], frozenset({"get_chat_service"}))
