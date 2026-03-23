"""
Theme-System – zentrale Theme-Infrastruktur.

ThemeManager, ThemeRegistry, ThemeDefinition, Design-Tokens.
"""

from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.manager import get_theme_manager
from app.gui.themes.theme_id_utils import (
    is_registered_theme_id,
    registered_theme_ids,
    theme_id_to_legacy_light_dark,
)
from app.gui.themes.tokens import ThemeTokens
from app.gui.themes.canonical_token_ids import ThemeTokenId, flat_key, all_flat_color_keys

__all__ = [
    "ThemeDefinition",
    "ThemeTokens",
    "ThemeTokenId",
    "flat_key",
    "all_flat_color_keys",
    "get_theme_manager",
    "is_registered_theme_id",
    "registered_theme_ids",
    "theme_id_to_legacy_light_dark",
]
