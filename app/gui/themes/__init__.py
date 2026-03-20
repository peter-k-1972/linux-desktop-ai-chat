"""
Theme-System – zentrale Theme-Infrastruktur.

ThemeManager, ThemeRegistry, ThemeDefinition, Design-Tokens.
"""

from app.gui.themes.manager import get_theme_manager
from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.tokens import ThemeTokens

__all__ = [
    "get_theme_manager",
    "ThemeDefinition",
    "ThemeTokens",
]
