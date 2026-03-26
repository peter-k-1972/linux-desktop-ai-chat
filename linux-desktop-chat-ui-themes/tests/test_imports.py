"""Smoke: distribution exposes app.ui_themes."""

from __future__ import annotations

from pathlib import Path

import app.ui_themes


def test_package_points_at_builtins() -> None:
    root = Path(app.ui_themes.__file__).resolve().parent
    mf = root / "builtins" / "light_default" / "manifest.json"
    assert mf.is_file(), f"missing {mf}"
