"""Theme id registry and legacy light/dark mapping."""

from app.gui.themes.theme_id_utils import (
    is_registered_theme_id,
    registered_theme_ids,
    theme_id_to_legacy_light_dark,
)


def test_registered_theme_ids_contains_workbench():
    ids = registered_theme_ids()
    assert "light_default" in ids
    assert "dark_default" in ids
    assert "workbench" in ids


def test_legacy_mapping():
    assert theme_id_to_legacy_light_dark("light_default") == "light"
    assert theme_id_to_legacy_light_dark("dark_default") == "dark"
    assert theme_id_to_legacy_light_dark("workbench") == "dark"


def test_is_registered_theme_id():
    assert is_registered_theme_id("workbench")
    assert not is_registered_theme_id("unknown_theme_xyz")
