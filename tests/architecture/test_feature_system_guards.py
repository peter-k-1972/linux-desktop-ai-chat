"""
Guards für Phase-1-Feature-System und Registrierungsschicht.

Siehe docs/architecture/FEATURE_SYSTEM.md
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.app_features_source_root import app_features_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT


def _iter_py_files_under(subdir: str):
    if subdir == "features":
        root = app_features_source_root()
    else:
        root = APP_ROOT.joinpath(*subdir.split("/"))
    if not root.is_dir():
        return
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _module_imports_app_top_levels(file_path: Path) -> set[str]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    tops: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app."):
                    parts = alias.name.split(".")
                    if len(parts) >= 2:
                        tops.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    tops.add(parts[1])
    return tops


@pytest.mark.architecture
@pytest.mark.contract
def test_app_features_does_not_import_gui():
    """Feature-Metadaten dürfen keinen Qt/GUI-Stack importieren."""
    violations = []
    fr = app_features_source_root()
    for path in _iter_py_files_under("features"):
        rel = path.relative_to(fr)
        tops = _module_imports_app_top_levels(path)
        if "gui" in tops:
            violations.append(str(Path("features") / rel))
    assert not violations, (
        f"app.features darf app.gui nicht importieren (Phase-1-Isolation). "
        f"Verletzungen: {violations}"
    )


def _file_imports_qt_top_level(path: Path) -> bool:
    """True bei Import/ImportFrom von PySide6, PyQt, shiboken (keine String-Vorkommen in Daten)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False
    qt_roots = frozenset({"PySide6", "PySide2", "PyQt5", "PyQt6", "shiboken6", "shiboken2"})
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = (alias.name or "").split(".", 1)[0]
                if root in qt_roots:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".", 1)[0]
                if root in qt_roots:
                    return True
    return False


@pytest.mark.architecture
@pytest.mark.contract
def test_app_features_does_not_import_qt():
    """app.features bleibt Qt-frei (wie ui_contracts); Manifest-Strings für PyPI-Namen sind erlaubt."""
    violations = []
    fr = app_features_source_root()
    for path in _iter_py_files_under("features"):
        if _file_imports_qt_top_level(path):
            violations.append(str(Path("features") / path.relative_to(fr)))
    assert not violations, f"app.features darf PySide6/PyQt nicht importieren: {violations}"


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_registration_avoids_direct_domain_packages():
    """
    Registrierungsschicht: keine direkten Imports von Domänen-Top-Packages.

    Domänen-UI bleibt unter gui.domains; hier nur Screen-Factories verdrahten.
    """
    forbidden = frozenset(
        {
            "chat",
            "chats",
            "rag",
            "workflows",
            "agents",
            "projects",
            "prompts",
            "persistence",
            "context",
            "services",
        }
    )
    violations = []
    for path in _iter_py_files_under("gui/registration"):
        tops = _module_imports_app_top_levels(path)
        bad = tops & forbidden
        if bad:
            violations.append((str(path.relative_to(APP_ROOT)), sorted(bad)))
    assert not violations, (
        "gui/registration darf keine direkten app.<domain>-Imports nutzen "
        f"(nutze gui.domains-*). Verletzungen: {violations}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_bootstraps_feature_registry_after_infrastructure():
    """Widget-Pfad: FeatureRegistry nach init_infrastructure (Phase-1-Reihenfolge)."""
    path = PROJECT_ROOT / "run_gui_shell.py"
    source = path.read_text(encoding="utf-8")
    assert "init_infrastructure" in source
    assert "set_feature_registry" in source
    assert "build_feature_registry_for_edition" in source or "build_default_feature_registry" in source
    pos_infra = source.find("init_infrastructure")
    pos_feat = source.find("set_feature_registry")
    assert pos_infra != -1 and pos_feat != -1 and pos_infra < pos_feat, (
        "run_gui_shell: init_infrastructure muss vor set_feature_registry stehen."
    )
