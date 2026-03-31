"""
Split-Readiness-Guards fuer ``app.persistence``.

- ``app.persistence`` muss ueber die installierte Paketwurzel aufloesbar sein.
- Das Paket bleibt frei von ``app.gui`` und Qt-Abhaengigkeiten.
- Zentrale Root-Dateien des Wheels muessen aus der Paketquelle lesbar sein.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.app_persistence_source_root import app_persistence_source_root

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


def _persistence_package_root() -> Path:
    return app_persistence_source_root()


def _iter_persistence_python_files() -> list[Path]:
    root = _persistence_package_root()
    return sorted(
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and not _SKIP_DIR_PARTS.intersection(p.parts)
    )


def _parse_tree(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


@pytest.mark.architecture
@pytest.mark.contract
def test_persistence_package_root_is_resolvable_via_installed_distribution() -> None:
    root = _persistence_package_root()
    assert root.is_dir(), f"app.persistence-Quellwurzel fehlt: {root}"


@pytest.mark.architecture
@pytest.mark.contract
def test_persistence_root_files_are_readable_from_wheel_source() -> None:
    root = _persistence_package_root()
    for rel in ("__init__.py", "session.py"):
        path = root / rel
        assert path.is_file(), f"Erwartete Root-Datei fehlt: {path}"
        text = path.read_text(encoding="utf-8")
        assert text.strip(), f"Root-Datei ist leer oder unlesbar: {path}"


@pytest.mark.architecture
@pytest.mark.contract
def test_persistence_domain_does_not_import_gui_or_qt() -> None:
    violations: list[tuple[str, list[str]]] = []
    root = _persistence_package_root()
    for py_path in _iter_persistence_python_files():
        tree = _parse_tree(py_path)
        if tree is None:
            continue
        hits: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name.startswith("app.gui"):
                        hits.append(name)
                    if name.split(".", 1)[0] in ("PySide6", "PySide2", "PySide"):
                        hits.append(name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith("app.gui"):
                    hits.append(mod)
                if mod.split(".", 1)[0] in ("PySide6", "PySide2", "PySide"):
                    hits.append(mod)
        if hits:
            rel = py_path.relative_to(root)
            violations.append((str(rel).replace("\\", "/"), hits))

    assert not violations, (
        "app.persistence darf app.gui oder PySide* nicht importieren. "
        f"Verletzungen: {violations}"
    )
