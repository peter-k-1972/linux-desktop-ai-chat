"""app.gui.themes.theme_loader"""

from __future__ import annotations

import json

import pytest

from app.gui.themes.theme_loader import ThemeLoadError, load_theme_file


def test_load_valid_json_dict(tmp_path) -> None:
    p = tmp_path / "t.json"
    data = {"name": "X", "colors": {"background": "#111111"}}
    p.write_text(json.dumps(data), encoding="utf-8")
    assert load_theme_file(str(p)) == data


def test_load_invalid_json_raises(tmp_path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{no json", encoding="utf-8")
    with pytest.raises(ThemeLoadError, match="JSON"):
        load_theme_file(str(p))


def test_load_missing_file_raises(tmp_path) -> None:
    with pytest.raises(ThemeLoadError, match="gelesen"):
        load_theme_file(str(tmp_path / "missing.json"))


def test_load_non_object_raises(tmp_path) -> None:
    p = tmp_path / "arr.json"
    p.write_text("[1]", encoding="utf-8")
    with pytest.raises(ThemeLoadError, match="Dict"):
        load_theme_file(str(p))
