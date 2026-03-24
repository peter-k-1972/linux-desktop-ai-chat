"""
QML python_bridge ViewModels dürfen keine Domänen-Services direkt importieren.

Ausnahme: WorkflowNotFoundError aus workflow_service (reines Exception-Symbol, kein Locator).
"""

from __future__ import annotations

import ast
from pathlib import Path


def _bridge_py_files() -> list[Path]:
    root = Path(__file__).resolve().parents[2] / "python_bridge"
    return sorted(p for p in root.rglob("*.py") if p.name != "__init__.py")


def _imports_from_services(tree: ast.AST) -> list[str]:
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.services."):
            names = ", ".join(a.name for a in node.names)
            out.append(f"from {node.module} import {names}")
    return out


def test_python_bridge_viewmodels_do_not_import_app_services():
    failures: list[str] = []
    for path in _bridge_py_files():
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        for imp in _imports_from_services(tree):
            if path.name == "workflow_viewmodel.py" and "WorkflowNotFoundError" in imp:
                continue
            failures.append(f"{path.relative_to(path.parents[2])}: {imp}")
    assert not failures, "Direct app.services imports in python_bridge:\n" + "\n".join(failures)
