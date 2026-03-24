"""ThemeRegistry — install, reload, remove."""

from __future__ import annotations

import json

import pytest

from app.gui.themes.registry import BUILTIN_THEME_IDS, ThemeRegistry
from app.gui.themes.theme_installer import ThemeInstallError


def _theme_file(name: str = "Reload Me") -> dict:
    return {
        "name": name,
        "colors": {
            "background": "#121212",
            "panel": "#1e1e1e",
            "text": "#e0e0e0",
            "accent": "#4aa3ff",
            "danger": "#ff5c5c",
        },
    }


@pytest.fixture
def isolated_user_dir(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.gui.themes.registry.user_themes_dir", lambda: tmp_path)


def test_reload_picks_up_dropped_file(isolated_user_dir, tmp_path) -> None:
    reg = ThemeRegistry()
    src = tmp_path / "one.json"
    src.write_text(json.dumps(_theme_file("One")), encoding="utf-8")
    tid = reg.install_theme(str(src))
    assert reg.get(tid) is not None
    (tmp_path / f"{tid}.json").unlink()
    reg.reload_themes()
    assert reg.get(tid) is None


def test_remove_builtin_forbidden(isolated_user_dir) -> None:
    reg = ThemeRegistry()
    for bid in BUILTIN_THEME_IDS:
        with pytest.raises(ThemeInstallError):
            reg.remove_theme(bid)


def test_remove_user_theme(isolated_user_dir, tmp_path) -> None:
    reg = ThemeRegistry()
    src = tmp_path / "x.json"
    src.write_text(json.dumps(_theme_file("Gone")), encoding="utf-8")
    tid = reg.install_theme(str(src))
    reg.remove_theme(tid)
    assert reg.get(tid) is None
    assert not (tmp_path / f"{tid}.json").exists()
