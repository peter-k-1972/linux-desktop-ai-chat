"""
Widgets/Panels sollen Presenter nicht per ``.run()`` ansprechen.

Stattdessen: :class:`app.ui_runtime.command_dispatcher.UICommandDispatcher` (``dispatch``).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.architecture.app_ui_runtime_source_root import app_ui_runtime_source_root
from tests.architecture.arch_guard_config import APP_ROOT

GUI_ROOT = APP_ROOT / "gui"

# Panel-, Widget- und Inspector-Module (GUI-Schicht, keine Workspaces).
_REL_PATH_PATTERN = re.compile(
    r"(^|/)(panels|widgets|inspector)(/|$)",
    re.IGNORECASE,
)


def _is_widget_layer_py(path: Path) -> bool:
    try:
        rel = path.relative_to(GUI_ROOT)
    except ValueError:
        return False
    s = str(rel).replace("\\", "/")
    if "/workspaces/" in f"/{s}/":
        return False
    return bool(_REL_PATH_PATTERN.search(s))


def _name_like_presenter_receiver(name: str) -> bool:
    """``presenter``, ``_foo_presenter``, ``list_presenter`` — nicht ``*_presenter_*``."""
    n = name.lower()
    return n == "presenter" or n.endswith("_presenter")


def _is_presenter_run_call(node: ast.Call) -> bool:
    """Nur direkter Empfänger von ``.run`` (kein rekursives Hochlaufen)."""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "run":
        return False
    v = func.value
    if isinstance(v, ast.Name):
        return _name_like_presenter_receiver(v.id)
    if isinstance(v, ast.Attribute):
        return _name_like_presenter_receiver(v.attr)
    return False


def _violations_in_tree(tree: ast.Module) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_presenter_run_call(node):
            lines.append(node.lineno)
    return sorted(set(lines))


@pytest.mark.architecture
def test_gui_widget_layer_avoids_direct_presenter_run() -> None:
    offenders: list[str] = []
    for path in sorted(GUI_ROOT.rglob("*.py")):
        if not path.is_file() or not _is_widget_layer_py(path):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        bad = _violations_in_tree(tree)
        if bad:
            rel = path.relative_to(APP_ROOT)
            offenders.append(f"{rel}: lines {bad}")
    assert not offenders, (
        "GUI panels/widgets/inspector must not call *.run() on presenter-like receivers; "
        "use UICommandDispatcher.dispatch instead.\n" + "\n".join(offenders)
    )


@pytest.mark.architecture
def test_command_dispatcher_module_exists() -> None:
    path = app_ui_runtime_source_root() / "command_dispatcher.py"
    assert path.is_file(), (
        "app.ui_runtime.command_dispatcher — Quelle in linux-desktop-chat-ui-runtime "
        "(editable install erforderlich)."
    )
