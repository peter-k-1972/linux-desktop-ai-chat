"""app.gui.themes.theme_validator"""

import pytest

from app.gui.themes.theme_validator import ThemeValidationError, validate_theme


def test_validate_minimal_ok() -> None:
    validate_theme(
        {
            "name": "Midnight Graphite",
            "colors": {
                "background": "#121212",
                "panel": "#1e1e1e",
                "text": "#e0e0e0",
                "accent": "#4aa3ff",
                "danger": "#ff5c5c",
            },
        },
    )


def test_validate_missing_name() -> None:
    with pytest.raises(ThemeValidationError, match="name"):
        validate_theme({"colors": {"background": "#111111"}})


def test_validate_missing_colors() -> None:
    with pytest.raises(ThemeValidationError, match="colors"):
        validate_theme({"name": "A"})


def test_validate_invalid_hex() -> None:
    with pytest.raises(ThemeValidationError, match="Hex"):
        validate_theme({"name": "A", "colors": {"background": "#gg0000"}})


def test_validate_short_hex_rejected() -> None:
    with pytest.raises(ThemeValidationError, match="Hex"):
        validate_theme({"name": "A", "colors": {"background": "#fff"}})
