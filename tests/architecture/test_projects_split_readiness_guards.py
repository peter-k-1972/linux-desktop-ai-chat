"""
Split-Readiness-Guards fuer ``app.projects``.

- ``app.projects`` bleibt GUI-/Service-frei und importiert weder ``app.gui``,
  ``app.services`` noch ``app.ui_application`` oder Qt.
- Außerhalb der Paket-Implementierung sind nur die flachen Public-Module
  ``app.projects.{lifecycle,milestones,controlling,models,monitoring_display}``
  kanonische Consumer-Pfade.
- Die aktuell einzige dokumentierte Außenkante innerhalb des Pakets ist
  ``app.projects.models`` -> ``app.chat.context_policies``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_projects_source_root import app_projects_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

_CANONICAL_PROJECTS_MODULES: frozenset[str] = frozenset(
    {
        "app.projects",
        "app.projects.controlling",
        "app.projects.lifecycle",
        "app.projects.milestones",
        "app.projects.models",
        "app.projects.monitoring_display",
    }
)

_SKIP_DIR_PARTS = frozenset(
    {
        ".venv",
        ".venv-commit2",
        ".venv-commit2-ui",
        "venv",
        "node_modules",
        ".git",
        "__pycache__",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)


def _iter_py_files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and not _SKIP_DIR_PARTS.intersection(p.parts)
    ]


def _projects_guard_scan_files() -> list[Path]:
    roots = [
        APP_ROOT,
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "tools",
        PROJECT_ROOT / "examples",
    ]
    scripts = PROJECT_ROOT / "scripts"
    if scripts.is_dir():
        roots.append(scripts)
    out: list[Path] = []
    for root in roots:
        if root.is_dir():
            out.extend(_iter_py_files(root))
    return out


def _projects_package_root() -> Path:
    """Installierter Quellbaum app.projects (Wheel/editable), nicht APP_ROOT/projects."""
    return app_projects_source_root()


def _iter_projects_python_files() -> list[Path]:
    root = _projects_package_root()
    return sorted(
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and not _SKIP_DIR_PARTS.intersection(p.parts)
    )


def _banned_projects_import_hits(file_path: Path) -> list[str]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []

    bad: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if (
                    name.startswith("app.gui")
                    or name.startswith("app.services")
                    or name.startswith("app.ui_application")
                ):
                    bad.append(name)
                root = name.split(".", 1)[0]
                if root in ("PySide6", "PySide2", "PySide"):
                    bad.append(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if (
                mod.startswith("app.gui")
                or mod.startswith("app.services")
                or mod.startswith("app.ui_application")
            ):
                bad.append(mod)
            root = mod.split(".", 1)[0] if mod else ""
            if root in ("PySide6", "PySide2", "PySide"):
                bad.append(mod)
    return bad


def _skip_as_projects_implementation(path: Path) -> bool:
    try:
        root = _projects_package_root().resolve()
        return path.resolve().is_relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return False


def _deep_projects_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _projects_guard_scan_files():
        if _skip_as_projects_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.projects"):
                continue
            if mod not in _CANONICAL_PROJECTS_MODULES:
                bad.append(f"{rel}: from {mod} import … (nicht kanonische Public-Surface)")
    return bad


def _private_projects_symbol_import_violations() -> list[str]:
    bad: list[str] = []
    for path in _projects_guard_scan_files():
        if _skip_as_projects_implementation(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(PROJECT_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level and node.level > 0:
                continue
            mod = node.module
            if not mod or not mod.startswith("app.projects"):
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name.startswith("_"):
                    bad.append(f"{rel}: from {mod} import {alias.name} (private API)")
    return bad


@pytest.mark.architecture
@pytest.mark.contract
def test_projects_domain_does_not_import_gui_services_ui_application_or_qt() -> None:
    violations: list[tuple[str, list[str]]] = []
    root = _projects_package_root()
    for py_path in _iter_projects_python_files():
        hits = _banned_projects_import_hits(py_path)
        if hits:
            rel = py_path.relative_to(root)
            violations.append((str(rel).replace("\\", "/"), hits))

    assert not violations, (
        "app.projects darf app.gui, app.services, app.ui_application oder PySide* "
        f"nicht importieren. Verletzungen: {violations}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_projects_imports_use_canonical_public_modules_only() -> None:
    bad = _deep_projects_import_violations()
    assert not bad, (
        "app.projects: außerhalb der Paket-Implementierung nur Paket-Root oder "
        "app.projects.{controlling,lifecycle,milestones,models,monitoring_display}. "
        "Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_private_projects_symbols_imported_outside_package() -> None:
    bad = _private_projects_symbol_import_violations()
    assert not bad, (
        "Keine Imports von führend-Unterstrich-Symbolen aus app.projects "
        "außerhalb des Pakets. Verstöße:\n" + "\n".join(bad)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_projects_models_only_documented_cross_domain_edge_is_chat_context_policy() -> None:
    models_path = _projects_package_root() / "models.py"
    tree = ast.parse(models_path.read_text(encoding="utf-8"))

    external_imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if not mod.startswith("app.") or mod.startswith("app.projects"):
                continue
            external_imports.add(mod)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if not name.startswith("app.") or name.startswith("app.projects"):
                    continue
                external_imports.add(name)

    assert external_imports == {"app.chat.context_policies"}, (
        "app.projects.models soll aktuell nur die dokumentierte Fachkante "
        "zu app.chat.context_policies halten. Gefunden: "
        f"{sorted(external_imports)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_projects_models_uses_chat_context_policy_as_enum_contract_only() -> None:
    models_path = _projects_package_root() / "models.py"
    tree = ast.parse(models_path.read_text(encoding="utf-8"))

    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "app.chat.context_policies":
            continue
        for alias in node.names:
            imported_names.add(alias.name)

    assert imported_names == {"ChatContextPolicy"}, (
        "app.projects.models soll aus app.chat.context_policies nur den "
        "Enum-Vertrag ChatContextPolicy importieren. Gefunden: "
        f"{sorted(imported_names)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_project_edit_dialog_uses_chat_context_policy_as_enum_contract_only() -> None:
    dialog_path = (
        APP_ROOT
        / "gui"
        / "domains"
        / "operations"
        / "projects"
        / "dialogs"
        / "project_edit_dialog.py"
    )
    tree = ast.parse(dialog_path.read_text(encoding="utf-8"))

    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "app.chat.context_policies":
            continue
        for alias in node.names:
            imported_names.add(alias.name)

    assert imported_names == {"ChatContextPolicy"}, (
        "project_edit_dialog soll aus app.chat.context_policies nur den "
        "Enum-Vertrag ChatContextPolicy importieren. Gefunden: "
        f"{sorted(imported_names)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_project_edit_dialog_policy_combo_values_match_chat_context_policy_values() -> None:
    dialog_path = (
        APP_ROOT
        / "gui"
        / "domains"
        / "operations"
        / "projects"
        / "dialogs"
        / "project_edit_dialog.py"
    )
    tree = ast.parse(dialog_path.read_text(encoding="utf-8"))

    returned_tuple_values: list[str | None] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_policy_combo_entries":
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Return) or not isinstance(sub.value, ast.List):
                continue
            for elt in sub.value.elts:
                if not isinstance(elt, ast.Tuple) or len(elt.elts) != 2:
                    continue
                raw_value = elt.elts[1]
                if isinstance(raw_value, ast.Constant) and raw_value.value is None:
                    returned_tuple_values.append(None)
                elif (
                    isinstance(raw_value, ast.Attribute)
                    and raw_value.attr == "value"
                    and isinstance(raw_value.value, ast.Attribute)
                    and isinstance(raw_value.value.value, ast.Name)
                    and raw_value.value.value.id == "ChatContextPolicy"
                ):
                    returned_tuple_values.append(raw_value.value.attr.lower())

    assert returned_tuple_values == [
        None,
        "default",
        "architecture",
        "debug",
        "exploration",
    ], (
        "_policy_combo_entries soll genau die dokumentierte Enum-Wertliste "
        "für Project-Policy-Auswahl abbilden. Gefunden: "
        f"{returned_tuple_values}"
    )
