"""
ThemeRegistry – Registrierung und Auflistung von Themes.
"""

from pathlib import Path

from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.tokens import ThemeTokens


def _themes_dir() -> Path:
    """Pfad zum themes-Verzeichnis."""
    return Path(__file__).parent


class ThemeRegistry:
    """
    Registry für verfügbare Themes.
    Lädt Themes aus Unterverzeichnissen von app/gui/themes/.
    """

    def __init__(self):
        self._themes: dict[str, ThemeDefinition] = {}
        self._load_builtin_themes()

    def _load_builtin_themes(self) -> None:
        """Lädt die eingebauten Themes (light_default, dark_default)."""
        self._themes["light_default"] = _build_light_default()
        self._themes["dark_default"] = _build_dark_default()

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
    """Light Default Theme."""
    tokens = ThemeTokens(
        color_bg="#f1f5f9",
        color_bg_surface="#ffffff",
        color_bg_muted="#f8fafc",
        color_bg_hover="#e2e8f0",
        color_bg_selected="#dbeafe",
        color_bg_input="#ffffff",
        color_text="#1f2937",
        color_text_secondary="#64748b",
        color_text_muted="#94a3b8",
        color_border="#e2e8f0",
        color_border_medium="#cbd5e1",
        color_accent="#1e40af",
        color_accent_hover="#1d4ed8",
        color_accent_bg="#dbeafe",
        color_nav_bg="#f8fafc",
        color_nav_selected_bg="#dbeafe",
        color_nav_selected_fg="#1e40af",
        color_monitoring_bg="#0f172a",
        color_monitoring_surface="#1e293b",
        color_monitoring_border="#334155",
        color_monitoring_text="#cbd5e1",
        color_monitoring_muted="#64748b",
        color_monitoring_accent="#34d399",
        color_monitoring_accent_bg="#065f46",
        color_qa_nav_selected_bg="#cffafe",
        color_qa_nav_selected_fg="#0e7490",
        color_text_inverse="#ffffff",
    )
    return ThemeDefinition(
        id="light_default",
        name="Light Default",
        tokens=tokens,
        extends=None,
    )


def _build_dark_default() -> ThemeDefinition:
    """Dark Default Theme."""
    tokens = ThemeTokens(
        color_bg="#1e293b",
        color_bg_surface="#0f172a",
        color_bg_muted="#334155",
        color_bg_hover="#475569",
        color_bg_selected="#1e3a5f",
        color_bg_input="#1e293b",
        color_text="#f1f5f9",
        color_text_secondary="#94a3b8",
        color_text_muted="#64748b",
        color_border="#334155",
        color_border_medium="#475569",
        color_accent="#60a5fa",
        color_accent_hover="#93c5fd",
        color_accent_bg="#1e3a5f",
        color_nav_bg="#1e293b",
        color_nav_selected_bg="#1e3a5f",
        color_nav_selected_fg="#93c5fd",
        color_monitoring_bg="#020617",
        color_monitoring_surface="#0f172a",
        color_monitoring_border="#334155",
        color_monitoring_text="#cbd5e1",
        color_monitoring_muted="#64748b",
        color_monitoring_accent="#34d399",
        color_monitoring_accent_bg="#065f46",
        color_qa_nav_selected_bg="#0e7490",
        color_qa_nav_selected_fg="#67e8f9",
        color_text_inverse="#ffffff",
    )
    return ThemeDefinition(
        id="dark_default",
        name="Dark Default",
        tokens=tokens,
        extends=None,
    )
