"""
Guardrail: ``RolloutRecordDialog`` — ``get_deployment_operations_service`` nur in Legacy-Combo-Ladepfad.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

DIALOG = APP_ROOT / "gui" / "domains" / "operations" / "deployment" / "dialogs" / "rollout_record_dialog.py"


def _class_body(tree: ast.Module, class_name: str) -> list[ast.stmt]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return list(node.body)
    raise AssertionError(f"class {class_name} not found")


def _function_def(body: list[ast.stmt], name: str) -> ast.FunctionDef | None:
    for item in body:
        if isinstance(item, ast.FunctionDef) and item.name == name:
            return item
    return None


def _calls_get_deployment_service(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name) and f.id == "get_deployment_operations_service":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "get_deployment_operations_service":
            return True
    return False


@pytest.mark.architecture
def test_rollout_record_dialog_service_only_in_reload_combos_legacy() -> None:
    tree = ast.parse(DIALOG.read_text(encoding="utf-8"))
    body = _class_body(tree, "RolloutRecordDialog")
    legacy = _function_def(body, "_reload_combos_legacy")
    assert legacy is not None
    assert _calls_get_deployment_service(legacy), "_reload_combos_legacy must load via deployment service."

    allowed_only = {"_reload_combos_legacy"}
    for item in body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if item.name in allowed_only:
            continue
        assert not _calls_get_deployment_service(item), (
            f"{item.name}() must not call get_deployment_operations_service "
            "(injected combo path is UI-only)."
        )