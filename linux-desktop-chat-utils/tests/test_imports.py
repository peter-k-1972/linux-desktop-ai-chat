"""Smoke: Paket ``app.utils`` und erwarteter Quellbaum."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_UTILS = _ROOT / "src" / "app" / "utils"

_EXPECTED_PY = frozenset(
    {
        "__init__.py",
        "paths.py",
        "datetime_utils.py",
        "env_loader.py",
    }
)


def test_utils_package_importable() -> None:
    import app.utils

    assert hasattr(app.utils, "__path__")


def test_utils_source_tree_has_expected_modules() -> None:
    names = {p.name for p in _UTILS.glob("*.py")}
    assert _EXPECTED_PY <= names
