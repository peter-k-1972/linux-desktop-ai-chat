"""Smoke-Tests für den Theme-Visualizer (Dev-Tool)."""

from app.devtools.theme_contrast import DEFAULT_CONTRAST_PAIRS
from app.devtools.theme_token_groups import TOKEN_GROUPS
from app.devtools.theme_visualizer_window import ThemeVisualizerWindow


def test_theme_visualizer_window_constructible(qapplication):
    win = ThemeVisualizerWindow()
    try:
        combo = win._theme_combo
        assert combo.count() >= 2
        ids = [combo.itemData(i) for i in range(combo.count())]
        assert "light_default" in ids
        assert "dark_default" in ids

        assert win.apply_selected_theme()

        assert win._token_layout.count() >= len(TOKEN_GROUPS)
        assert win._contrast_list.count() == len(DEFAULT_CONTRAST_PAIRS)

        assert win._preview_scroll.widget() is not None
    finally:
        win.close()
