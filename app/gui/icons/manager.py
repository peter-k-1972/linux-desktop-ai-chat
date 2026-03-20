"""
IconManager – zentrale Icon-Verwaltung.

Lädt SVG-Icons, unterstützt Theme-Farben, Caching.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, Qt

from app.gui.icons.registry import IconRegistry
from app.utils.paths import get_icons_dir

if TYPE_CHECKING:
    from app.gui.themes.manager import ThemeManager


def _icons_base_path() -> Path:
    """Basis-Pfad zum Icons-Verzeichnis (assets/icons/svg)."""
    return get_icons_dir() / "svg"


def _get_theme_color(token: str = "color_text") -> str:
    """Liefert die aktuelle Theme-Farbe, falls ThemeManager verfügbar."""
    defaults: dict[str, str] = {
        "color_text": "#1f2937",
        "color_monitoring_text": "#cbd5e1",
    }
    try:
        from app.gui.themes import get_theme_manager

        mgr = get_theme_manager()
        tokens = mgr.get_tokens()
        return tokens.get(token, defaults.get(token, "#1f2937"))
    except Exception:
        return defaults.get(token, "#1f2937")


def _load_svg_content(name: str) -> str | None:
    """Lädt den SVG-Inhalt einer Icon-Datei."""
    rel = IconRegistry.get_path(name)
    if not rel:
        return None
    path = _icons_base_path() / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _colorize_svg(svg: str, color: str) -> str:
    """
    Ersetzt currentColor und fill/stroke ohne Farbe durch die Zielfarbe.
    SVG sollte stroke="currentColor" oder fill="currentColor" verwenden.
    """
    # currentColor ersetzen
    result = svg.replace("currentColor", color)
    # Fallback: stroke/fill ohne Wert in path/line etc. – SVG-Struktur beibehalten
    return result


class IconManager:
    """
    Zentraler Icon-Manager.
    - Lädt SVG aus assets/icons/svg/{category}/{name}.svg (via get_icons_dir)
    - Unterstützt Theme-Farben
    - Caching nach (name, size, color)
    """

    _cache: dict[tuple[str, int, str], QIcon] = {}
    _default_size: int = 24

    @classmethod
    def get(
        cls,
        name: str,
        size: int | None = None,
        color: str | None = None,
        color_token: str = "color_text",
    ) -> QIcon:
        """
        Liefert ein QIcon für den angegebenen Namen.

        Args:
            name: Icon-Name (z.B. "dashboard", "chat", "add")
            size: Zielgröße in px (Standard: 24)
            color: Hex-Farbe (z.B. "#1f2937"). None = Theme-Farbe
            color_token: Theme-Token für Farbe, wenn color=None

        Returns:
            QIcon, oder leeres QIcon wenn nicht gefunden
        """
        size = size or cls._default_size
        color = color or _get_theme_color(color_token)
        key = (name, size, color)

        if key in cls._cache:
            return cls._cache[key]

        svg_content = _load_svg_content(name)
        if not svg_content:
            return QIcon()

        colored = _colorize_svg(svg_content, color)
        data = QByteArray(colored.encode("utf-8"))

        renderer = QSvgRenderer(data)
        if not renderer.isValid():
            return QIcon()

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        icon = QIcon(pixmap)
        cls._cache[key] = icon
        return icon

    @classmethod
    def clear_cache(cls) -> None:
        """Leert den Icon-Cache. Nach Theme-Wechsel aufrufen."""
        cls._cache.clear()

    @classmethod
    def has(cls, name: str) -> bool:
        """Prüft, ob ein Icon mit dem Namen existiert."""
        rel = IconRegistry.get_path(name)
        if not rel:
            return False
        path = _icons_base_path() / rel
        return path.exists()


# Singleton-Zugriff
_manager: IconManager | None = None


def get_icon_manager() -> IconManager:
    """Liefert die IconManager-Klasse (statische Methoden)."""
    return IconManager
