"""
ThemeRegistry – Registrierung und Auflistung von Themes.

Built-in themes are authored as :class:`SemanticPalette` profiles, resolved to
:class:`ThemeTokens` for QSS (see :mod:`palette_resolve`).
"""

from app.gui.themes.builtin_semantic_profiles import (
    dark_semantic_profile,
    light_semantic_profile,
    workbench_semantic_profile,
)
from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.palette_resolve import semantic_palette_to_theme_tokens


class ThemeRegistry:
    """
    Registry für verfügbare Themes.
    Lädt Themes aus Unterverzeichnissen von app/gui/themes/.
    """

    def __init__(self):
        self._themes: dict[str, ThemeDefinition] = {}
        self._load_builtin_themes()

    def _load_builtin_themes(self) -> None:
        """Lädt die eingebauten Themes (light_default, dark_default, workbench)."""
        self._themes["light_default"] = _build_light_default()
        self._themes["dark_default"] = _build_dark_default()
        self._themes["workbench"] = _build_workbench()

    def register(self, theme: ThemeDefinition) -> None:
        """Registriert ein Theme."""
        self._themes[theme.id] = theme

    def get(self, theme_id: str) -> ThemeDefinition | None:
        """Liefert ein Theme nach ID."""
        return self._themes.get(theme_id)

    def list_themes(self) -> list[tuple[str, str]]:
        """Liefert [(id, name), ...] aller registrierten Themes."""
        return [(t.id, t.name) for t in self._themes.values()]

    def __contains__(self, theme_id: str) -> bool:
        return theme_id in self._themes


def _build_light_default() -> ThemeDefinition:
    p = light_semantic_profile()
    return ThemeDefinition(
        id="light_default",
        name="Light",
        tokens=semantic_palette_to_theme_tokens("light_default", p),
        extends=None,
    )


def _build_dark_default() -> ThemeDefinition:
    p = dark_semantic_profile()
    return ThemeDefinition(
        id="dark_default",
        name="Dark",
        tokens=semantic_palette_to_theme_tokens("dark_default", p),
        extends=None,
    )


def _build_workbench() -> ThemeDefinition:
    p = workbench_semantic_profile()
    return ThemeDefinition(
        id="workbench",
        name="Workbench",
        tokens=semantic_palette_to_theme_tokens("workbench", p),
        extends=None,
    )
