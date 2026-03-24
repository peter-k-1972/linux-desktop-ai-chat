"""
Deployment-Edit-Dialoge: ``get_project_service`` nur noch im Legacy-Zweig ``_load_projects_legacy``.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

TARGET = APP_ROOT / "gui" / "domains" / "operations" / "deployment" / "dialogs" / "target_edit_dialog.py"
RELEASE = APP_ROOT / "gui" / "domains" / "operations" / "deployment" / "dialogs" / "release_edit_dialog.py"


def _func_names_with_project_service(tree: ast.Module) -> set[str]:
    bad: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            for sub in ast.walk(item):
                if not isinstance(sub, ast.Call):
                    continue
                f = sub.func
                if isinstance(f, ast.Attribute) and f.attr == "get_project_service":
                    bad.add(item.name)
                if isinstance(f, ast.Name) and f.id == "get_project_service":
                    bad.add(item.name)
    return bad


@pytest.mark.architecture
def test_target_edit_dialog_project_service_only_in_legacy_loader() -> None:
    tree = ast.parse(TARGET.read_text(encoding="utf-8"))
    assert _func_names_with_project_service(tree) == {"_load_projects_legacy"}


@pytest.mark.architecture
def test_release_edit_dialog_project_service_only_in_legacy_loader() -> None:
    tree = ast.parse(RELEASE.read_text(encoding="utf-8"))
    assert _func_names_with_project_service(tree) == {"_load_projects_legacy"}
