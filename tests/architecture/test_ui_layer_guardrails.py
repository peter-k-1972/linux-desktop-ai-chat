"""
Guardrails fuer das UI-System und die verbleibenden Hybrid-Raender.

Zusaetzlich: ``test_ui_contracts_public_surface_guard`` — keine ``_*``-Imports aus
``app.ui_contracts`` ausserhalb des Pakets (Host-Repo-Scan; installierter Tree nicht im Walk).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_ui_contracts_source_root import app_ui_contracts_source_root
from tests.architecture.app_ui_runtime_source_root import app_ui_runtime_source_root
from tests.architecture.app_ui_themes_source_root import app_ui_themes_source_root
from tests.architecture.arch_guard_config import APP_ROOT

UI_RUNTIME_THEME_MODULES = (
    "manifest_models.py",
    "theme_loader.py",
    "theme_registry.py",
    "base_runtime.py",
)
REMOVED_ROOT_STARTUP_SHIMS = (
    "app.gui_bootstrap",
    "app.gui_registry",
    "app.gui_capabilities",
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
                if alias.name == forbidden_prefix or alias.name.startswith(forbidden_prefix + "."):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and (
                node.module == forbidden_prefix or node.module.startswith(forbidden_prefix + ".")
            ):
                hits.append(node.module)
    return hits


def _file_imports_with_prefixes(file_path: Path, prefixes: tuple[str, ...]) -> list[str]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name == pref or alias.name.startswith(pref + ".") for pref in prefixes):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod == pref or mod.startswith(pref + ".") for pref in prefixes):
                hits.append(mod)
    return hits


def _collect_forbidden_bridge_imports(root: Path, prefixes: tuple[str, ...]) -> list[tuple[str, list[str]]]:
    violations = []
    for path in _iter_py(root):
        hits = _file_imports_with_prefixes(path, prefixes)
        if hits:
            violations.append((str(path.relative_to(APP_ROOT)), sorted(set(hits))))
    return violations


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
    uc_root = app_ui_contracts_source_root()
    violations = []
    for path in _iter_py(uc_root):
        bad = _collect_qt_imports(path)
        if bad:
            violations.append((str(path.relative_to(uc_root)), bad))
    assert not violations, f"ui_contracts muss Qt-frei bleiben: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_themes_python_has_no_app_services():
    """Theme-Baum: Python-Dateien dürfen app.services nicht importieren."""
    violations = []
    ui_root = app_ui_themes_source_root()
    for path in _iter_py(ui_root):
        for hit in _file_imports_module(path, "app.services"):
            violations.append((str(path.relative_to(ui_root)), hit))
    assert not violations, f"ui_themes darf app.services nicht importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_runtime_core_theme_modules_avoid_services():
    """Kern-Theme-Loader dürfen keine Service-Schicht importieren (Cutover-Schutz)."""
    root = app_ui_runtime_source_root()
    violations = []
    for name in UI_RUNTIME_THEME_MODULES:
        path = root / name
        if not path.is_file():
            continue
        for hit in _file_imports_module(path, "app.services"):
            violations.append((str(path.relative_to(root)), hit))
    widgets = root / "widgets" / "widgets_runtime.py"
    if widgets.is_file():
        for hit in _file_imports_module(widgets, "app.services"):
            violations.append((str(widgets.relative_to(root)), hit))
    qml_pkg = root / "qml"
    if qml_pkg.is_dir():
        for path in qml_pkg.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            for hit in _file_imports_module(path, "app.services"):
                violations.append((str(path.relative_to(root)), hit))
    assert not violations, f"ui_runtime Theme-Kern importiert app.services: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_application_has_no_direct_gui_imports():
    root = APP_ROOT / "ui_application"
    violations = _collect_forbidden_bridge_imports(root, ("app.gui",))
    assert not violations, f"ui_application darf app.gui nicht direkt importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_workspace_presets_has_no_direct_gui_imports():
    root = APP_ROOT / "workspace_presets"
    violations = _collect_forbidden_bridge_imports(root, ("app.gui",))
    assert not violations, f"workspace_presets darf app.gui nicht direkt importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_global_overlay_has_no_direct_gui_imports():
    root = APP_ROOT / "global_overlay"
    violations = _collect_forbidden_bridge_imports(root, ("app.gui",))
    assert not violations, f"global_overlay darf app.gui nicht direkt importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_application_avoids_root_gui_bridges():
    root = APP_ROOT / "ui_application"
    violations = _collect_forbidden_bridge_imports(
        root,
        REMOVED_ROOT_STARTUP_SHIMS,
    )
    assert not violations, f"ui_application darf keine entfernten Root-Startup-Shims importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_workspace_presets_avoids_root_gui_bridges():
    root = APP_ROOT / "workspace_presets"
    violations = _collect_forbidden_bridge_imports(
        root,
        REMOVED_ROOT_STARTUP_SHIMS,
    )
    assert not violations, f"workspace_presets darf keine entfernten Root-Startup-Shims importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_global_overlay_avoids_root_gui_bridges():
    root = APP_ROOT / "global_overlay"
    violations = _collect_forbidden_bridge_imports(
        root,
        REMOVED_ROOT_STARTUP_SHIMS,
    )
    assert not violations, f"global_overlay darf keine entfernten Root-Startup-Shims importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_help_gui_bridge_is_limited_to_defined_ui_components():
    root = APP_ROOT / "help"
    violations = []
    for path in _iter_py(root):
        rel = str(path.relative_to(APP_ROOT))
        hits = _file_imports_module(path, "app.gui")
        if not hits:
            continue
        if rel == "help/ui_components.py":
            allowed = {
                "app.gui.components.doc_search_panel",
                "app.gui.components.markdown_widgets",
                "app.gui.shared.markdown",
            }
            unexpected = sorted(set(hit for hit in hits if hit not in allowed))
            if unexpected:
                violations.append((rel, unexpected))
            continue
        violations.append((rel, sorted(set(hits))))
    assert not violations, f"help darf app.gui nur ueber help/ui_components.py nutzen: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_devtools_gui_bridge_stays_within_themes():
    root = APP_ROOT / "devtools"
    violations = []
    for path in _iter_py(root):
        rel = str(path.relative_to(APP_ROOT))
        hits = _file_imports_with_prefixes(path, ("app.gui",))
        unexpected = sorted(
            set(hit for hit in hits if not (hit == "app.gui.themes" or hit.startswith("app.gui.themes.")))
        )
        if unexpected:
            violations.append((rel, unexpected))
    assert not violations, f"devtools darf app.gui nur ueber app.gui.themes anbinden: {violations}"
