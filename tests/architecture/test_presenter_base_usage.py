"""
Guardrail: optionale Nutzung von ``app.ui_application.presenter_base``.

- Neue Infrastruktur ist verfügbar (``BasePresenter.run``).
- Bestehende Presenter importieren ``presenter_base`` nicht (keine stillschweigende Migration).
"""

from __future__ import annotations

import ast
import importlib

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PRESENTERS_DIR = APP_ROOT / "ui_application" / "presenters"


def _imports_presenter_base(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "app.ui_application.presenter_base":
                    return True
                if alias.name.endswith(".presenter_base"):
                    return True
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "app.ui_application.presenter_base":
                return True
            if mod.endswith(".presenter_base"):
                return True
    return False


@pytest.mark.architecture
def test_presenter_base_module_exposes_run_pipeline() -> None:
    mod = importlib.import_module("app.ui_application.presenter_base")
    cls = getattr(mod, "BasePresenter", None)
    assert cls is not None
    assert callable(getattr(cls, "run", None))


@pytest.mark.architecture
def test_existing_presenters_do_not_import_presenter_base() -> None:
    offenders: list[str] = []
    for path in sorted(PRESENTERS_DIR.glob("*_presenter.py")):
        if path.name == "base_presenter.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if _imports_presenter_base(tree):
            offenders.append(str(path.relative_to(APP_ROOT)))
    assert not offenders, (
        "Existing presenters must not import app.ui_application.presenter_base "
        f"(found: {offenders})"
    )
