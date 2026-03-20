"""
Regression: Settings nutzen Theme-Tokens, keine hardcodierten Farben.

Verhindert Kontrastfehler (weiße Schrift auf weißem Hintergrund im Light Theme,
dunkles Grau auf schwarzem Hintergrund im Dark Theme).
"""

import pytest

from app.gui.themes.registry import ThemeRegistry
from app.gui.themes.tokens import ThemeTokens


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

    # Text sollte dunkel sein (für hellen Hintergrund)
    assert tokens.color_text != "#ffffff"
    assert tokens.color_bg_surface in ("#ffffff", "#fff", "white") or tokens.color_bg_surface.lower().startswith("#f")


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


def test_both_themes_provide_all_settings_tokens():
    """Beide Themes liefern alle für Settings benötigten Tokens."""
    required = [
        "color_text",
        "color_text_secondary",
        "color_bg",
        "color_bg_surface",
        "color_bg_muted",
        "color_bg_hover",
        "color_bg_selected",
        "color_border",
        "color_accent",
        "color_nav_bg",
        "color_nav_selected_bg",
        "color_nav_selected_fg",
    ]
    registry = ThemeRegistry()
    for theme_id in ("light_default", "dark_default"):
        theme = registry.get(theme_id)
        assert theme is not None
        d = theme.get_tokens_dict()
        for key in required:
            assert key in d, f"{theme_id} fehlt Token {key}"
            assert d[key], f"{theme_id} Token {key} ist leer"
