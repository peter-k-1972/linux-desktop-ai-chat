"""
Guardrails für das neue UI-System (ui_contracts / ui_themes / ui_runtime).

Verschärfung später: z. B. ui_application ohne direkte gui-imports (Ausnahmeliste).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

UI_CONTRACTS = APP_ROOT / "ui_contracts"
UI_THEMES = APP_ROOT / "ui_themes"
UI_RUNTIME_THEME_MODULES = (
    "manifest_models.py",
    "theme_loader.py",
    "theme_registry.py",
    "base_runtime.py",
)


def _iter_py(root: Path):
    if not root.exists():
        return
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def _file_imports_module(file_path: Path, forbidden_prefix: str) -> list[str]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(forbidden_prefix):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(forbidden_prefix):
                hits.append(node.module)
    return hits


def _forbidden_qt_roots() -> tuple[str, ...]:
    return ("PySide6", "PyQt5", "PyQt6", "PySide2", "shiboken6", "shiboken2")


def _collect_qt_imports(file_path: Path) -> list[str]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return []
    hits: list[str] = []
    roots = _forbidden_qt_roots()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(r) for r in roots):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(node.module.startswith(r) for r in roots):
                hits.append(node.module)
    return hits


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_contracts_has_no_qt_imports():
    violations = []
    for path in _iter_py(UI_CONTRACTS):
        bad = _collect_qt_imports(path)
        if bad:
            violations.append((str(path.relative_to(APP_ROOT)), bad))
    assert not violations, f"ui_contracts muss Qt-frei bleiben: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_themes_python_has_no_app_services():
    """Theme-Baum: Python-Dateien dürfen app.services nicht importieren."""
    violations = []
    for path in _iter_py(UI_THEMES):
        for hit in _file_imports_module(path, "app.services"):
            violations.append((str(path.relative_to(APP_ROOT)), hit))
    assert not violations, f"ui_themes darf app.services nicht importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_runtime_core_theme_modules_avoid_services():
    """Kern-Theme-Loader dürfen keine Service-Schicht importieren (Cutover-Schutz)."""
    root = APP_ROOT / "ui_runtime"
    violations = []
    for name in UI_RUNTIME_THEME_MODULES:
        path = root / name
        if not path.is_file():
            continue
        for hit in _file_imports_module(path, "app.services"):
            violations.append((name, hit))
    widgets = root / "widgets" / "widgets_runtime.py"
    if widgets.is_file():
        for hit in _file_imports_module(widgets, "app.services"):
            violations.append((str(widgets.relative_to(APP_ROOT)), hit))
    qml_pkg = root / "qml"
    if qml_pkg.is_dir():
        for path in qml_pkg.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            for hit in _file_imports_module(path, "app.services"):
                violations.append((str(path.relative_to(APP_ROOT)), hit))
    assert not violations, f"ui_runtime Theme-Kern importiert app.services: {violations}"
