"""
IconManager – zentrale Icon-Verwaltung.

Lädt SVGs mit ``currentColor``, färbt über Theme-Tokens (States), cached pro
Theme/Name/State/Größe/Auflösungsfarbe.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.gui.icons.icon_states import ICON_STATE_TO_TOKEN, normalize_icon_state
from app.gui.icons.registry import IconRegistry
from app.gui.themes.canonical_token_ids import ThemeTokenId, flat_key
from app.utils.paths import get_icons_dir

if TYPE_CHECKING:
    pass


def _icons_base_path() -> Path:
    return get_icons_dir() / "svg"


def _fallback_tokens_dict() -> dict[str, str]:
    try:
        from app.gui.themes.registry import ThemeRegistry

        td = ThemeRegistry().get("light_default")
        if td:
            return td.get_tokens_dict()
    except Exception:
        pass
    return {}


def _resolve_color_string(
    *,
    state: str,
    color: str | None,
    color_token: str | None,
) -> str:
    if color:
        return color
    st = normalize_icon_state(state)
    try:
        from app.gui.themes import get_theme_manager

        mgr = get_theme_manager()
        if color_token:
            t = color_token.strip()
            if t:
                c = mgr.color(t)
                if c:
                    return c
        canon = ICON_STATE_TO_TOKEN.get(st, ThemeTokenId.FG_SECONDARY)
        c = mgr.color(canon)
        if c:
            return c
    except Exception:
        pass
    d = _fallback_tokens_dict()
    if color_token:
        t = color_token.strip()
        if t:
            fk = flat_key(t) if "." in t else t
            v = d.get(fk) or d.get(t)
            if v:
                return v
    canon = ICON_STATE_TO_TOKEN.get(st, ThemeTokenId.FG_SECONDARY)
    fk = flat_key(canon)
    return d.get(fk) or d.get(canon) or ""


def _current_theme_id() -> str:
    try:
        from app.gui.themes import get_theme_manager

        return get_theme_manager().get_current_id()
    except Exception:
        return ""


def _load_svg_content(name: str) -> str | None:
    from app.gui.icons.icon_registry import get_resource_svg_path

    res = get_resource_svg_path(name)
    if res is not None and res.exists():
        return res.read_text(encoding="utf-8")
    rel = IconRegistry.get_path(name)
    if not rel:
        return None
    path = _icons_base_path() / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _tint_svg_with_color(svg: str, color: str) -> str:
    """Ersetzt ``currentColor`` durch die aufgelöste Theme-Farbe."""
    if not color:
        return svg
    return svg.replace("currentColor", color)


class IconManager:
    """
    Zentraler Icon-Manager: ``resources/icons`` zuerst, dann ``assets/icons/svg``.
    Cache-Key: (theme_id, name, size, state, color_token, resolved_color).
    """

    _cache: dict[tuple[str, str, int, str, str | None, str], QIcon] = {}
    _default_size: int = 24

    @classmethod
    def get(
        cls,
        name: str,
        size: int | None = None,
        *,
        state: str = "default",
        color: str | None = None,
        color_token: str | None = None,
    ) -> QIcon:
        size = int(size or cls._default_size)
        st = normalize_icon_state(state)
        resolved = _resolve_color_string(state=st, color=color, color_token=color_token)
        if not resolved:
            resolved = "#6b7280"
        ct_key = color_token.strip() if color_token else None
        theme_id = _current_theme_id()
        key = (theme_id, name, size, st, ct_key, resolved)

        cached = cls._cache.get(key)
        if cached is not None:
            return cached

        svg_content = _load_svg_content(name)
        if not svg_content:
            return QIcon()

        tinted = _tint_svg_with_color(svg_content, resolved)
        data = QByteArray(tinted.encode("utf-8"))
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
        cls._cache.clear()

    @classmethod
    def has(cls, name: str) -> bool:
        from app.gui.icons.icon_registry import get_resource_svg_path

        p = get_resource_svg_path(name)
        if p is not None and p.exists():
            return True
        rel = IconRegistry.get_path(name)
        if not rel:
            return False
        return (_icons_base_path() / rel).exists()


_manager: IconManager | None = None


def get_icon_manager() -> IconManager:
    return IconManager
