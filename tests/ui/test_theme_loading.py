"""QSS-Loader ersetzt Token-Platzhalter."""

from app.gui.themes.loader import load_stylesheet
from app.gui.themes.registry import ThemeRegistry


def test_load_stylesheet_resolves_placeholders(qapplication):
    reg = ThemeRegistry()
    theme = reg.get("light_default")
    assert theme is not None
    css = load_stylesheet(theme)
    assert len(css) > 100
    # Unbekannte Platzhalter bleiben {{…}} — bekannte Farb-Tokens sollten ersetzt sein
    assert "{{color_text}}" not in css
    assert "{{color_bg}}" not in css
