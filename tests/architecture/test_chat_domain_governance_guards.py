"""
Architektur-Guard: Chat-Domain (app.chat) ohne GUI-/Presenter-Rueckkante.

Regel: app/chat importiert weder app.gui, app.ui_application noch Qt (PySide*).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT


def _banned_import_hits(file_path: Path) -> list[str]:
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    bad: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app.gui") or name.startswith("app.ui_application"):
                    bad.append(name)
                root = name.split(".", 1)[0]
                if root in ("PySide6", "PySide2", "PySide"):
                    bad.append(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith("app.gui") or mod.startswith("app.ui_application"):
                bad.append(mod)
            root = mod.split(".", 1)[0] if mod else ""
            if root in ("PySide6", "PySide2", "PySide"):
                bad.append(mod)
    return bad


def _iter_chat_python_files() -> list[Path]:
    chat_root = APP_ROOT / "chat"
    out: list[Path] = []
    for path in sorted(chat_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        out.append(path)
    return out


@pytest.mark.architecture
@pytest.mark.contract
def test_chat_domain_does_not_import_gui_ui_application_or_qt() -> None:
    violations: list[tuple[str, list[str]]] = []
    for py_path in _iter_chat_python_files():
        hits = _banned_import_hits(py_path)
        if hits:
            rel = py_path.relative_to(APP_ROOT)
            violations.append((str(rel).replace("\\", "/"), hits))

    assert not violations, (
        "app.chat darf app.gui, app.ui_application oder PySide* nicht importieren. "
        f"Verletzungen: {violations}"
    )
