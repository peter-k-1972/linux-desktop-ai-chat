"""app.gui.themes.theme_installer"""

from __future__ import annotations

import json

import pytest

from app.gui.themes.registry import ThemeRegistry
from app.gui.themes.theme_installer import ThemeInstallError, ThemeInstaller


def _valid_theme() -> dict:
    return {
        "name": "Imported Slice",
        "version": "1.0",
        "author": "Test",
        "colors": {
            "background": "#121212",
            "panel": "#1e1e1e",
            "text": "#e0e0e0",
            "accent": "#4aa3ff",
            "danger": "#ff5c5c",
        },
        "fonts": {"default": "Inter", "size": 13},
        "metrics": {"radius": 6, "spacing": 8},
    }


@pytest.fixture
def isolated_user_dir(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.gui.themes.registry.user_themes_dir", lambda: tmp_path)


def test_installer_delegates_to_registry(isolated_user_dir, tmp_path) -> None:
    src = tmp_path / "src.json"
    src.write_text(json.dumps(_valid_theme()), encoding="utf-8")
    reg = ThemeRegistry()
    n_before = len(reg.list_themes())
    tid = ThemeInstaller(reg).install_theme(str(src))
    assert tid.startswith("user_")
    assert len(reg.list_themes()) == n_before + 1
    assert reg.get(tid) is not None
    assert (tmp_path / f"{tid}.json").is_file()


def test_installer_missing_file(isolated_user_dir, tmp_path) -> None:
    reg = ThemeRegistry()
    with pytest.raises(ThemeInstallError, match="nicht gefunden"):
        ThemeInstaller(reg).install_theme(str(tmp_path / "nope.json"))
