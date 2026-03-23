"""
Regression: Settings nutzen Theme-Tokens, keine hardcodierten Farben.

Verhindert Kontrastfehler (weiße Schrift auf weißem Hintergrund im Light Theme,
dunkles Grau auf schwarzem Hintergrund im Dark Theme).
"""

import pytest

from app.gui.themes import all_flat_color_keys
from app.gui.themes.contrast import contrast_ratio
from app.gui.themes.registry import ThemeRegistry


def test_light_theme_has_readable_text_colors():
    """Light Theme: Text-Farben sind dunkel auf hellem Hintergrund."""
    registry = ThemeRegistry()
    theme = registry.get("light_default")
    assert theme is not None
    tokens = theme.tokens

    assert tokens.color_text
    assert tokens.color_text_secondary
    assert tokens.color_bg_surface
    assert tokens.color_bg

    # Text sollte dunkel sein (für hellen Hintergrund); Surface kann getöntes OKLCH-Neutral sein
    assert tokens.color_text != "#ffffff"
    assert contrast_ratio(tokens.color_text, tokens.color_bg_surface) >= 4.5


def test_dark_theme_has_readable_text_colors():
    """Dark Theme: Text-Farben sind hell auf dunklem Hintergrund."""
    registry = ThemeRegistry()
    theme = registry.get("dark_default")
    assert theme is not None
    tokens = theme.tokens

    assert tokens.color_text
    assert tokens.color_bg_surface

    # Text sollte hell sein
    assert tokens.color_text != "#000000"
    assert tokens.color_text != "#1f2937"


def test_all_builtin_themes_provide_all_settings_tokens():
    """Alle eingebauten Themes liefern alle für Settings benötigten Tokens."""
    required = [
        "color_text",
        "color_text_secondary",
        "color_bg",
        "color_bg_surface",
        "color_bg_muted",
        "color_bg_elevated",
        "color_bg_hover",
        "color_bg_selected",
        "color_border",
        "color_border_medium",
        "color_border_strong",
        "color_accent",
        "color_focus_ring",
        "color_fg_on_selected",
        "color_text_disabled",
        "color_nav_bg",
        "color_nav_selected_bg",
        "color_nav_selected_fg",
        "color_console_info",
        "color_console_warning",
        "color_console_error",
        "color_console_success",
    ]
    registry = ThemeRegistry()
    for theme_id, _name in registry.list_themes():
        theme = registry.get(theme_id)
        assert theme is not None
        d = theme.get_tokens_dict()
        for key in required:
            assert key in d, f"{theme_id} fehlt Token {key}"
            assert d[key], f"{theme_id} Token {key} ist leer"


def test_builtin_themes_have_full_spec_color_keys():
    """THEME_TOKEN_SPEC: alle deklarierten Farb-Flat-Keys sind befüllt."""
    registry = ThemeRegistry()
    keys = sorted(all_flat_color_keys())
    assert keys
    for theme_id, _name in registry.list_themes():
        theme = registry.get(theme_id)
        assert theme is not None
        d = theme.get_tokens_dict()
        for key in keys:
            assert key in d, f"{theme_id} fehlt Spec-Key {key}"
            assert (d.get(key) or "").strip(), f"{theme_id} Spec-Key {key} leer"
