"""
Resolve design values for Python code: colors from ThemeManager, metrics local.

This is intentionally small — no full migration of ``ThemeTokens`` yet.
"""

from __future__ import annotations

from typing import ClassVar

from app.gui.theme import design_metrics as dm
from app.gui.theme.design_tokens import IconSizeId, RadiusId, SpaceId, TextSizeId
from app.gui.themes.canonical_token_ids import flat_key


class DesignTokenRegistry:
    """
    Central lookup for spacing, type sizes, radii, and icon box sizes (int px).

    Colors: delegate to ``ThemeManager.color`` (canonical or flat id).
    """

    _SPACE_MAP: ClassVar[dict[str, int]] = {
        SpaceId.X2S: dm.SPACE_2XS_PX,
        SpaceId.XS: dm.SPACE_XS_PX,
        SpaceId.SM: dm.SPACE_SM_PX,
        SpaceId.MD: dm.SPACE_MD_PX,
        SpaceId.LG: dm.SPACE_LG_PX,
        SpaceId.XL: dm.SPACE_XL_PX,
        SpaceId.X2L: dm.SPACE_2XL_PX,
    }

    _TEXT_MAP: ClassVar[dict[str, int]] = {
        TextSizeId.XS: dm.TEXT_XS_PX,
        TextSizeId.SM: dm.TEXT_SM_PX,
        TextSizeId.BASE: dm.TEXT_BASE_PX,
        TextSizeId.MD: dm.TEXT_MD_PX,
        TextSizeId.LG: dm.TEXT_LG_PX,
        TextSizeId.XL: dm.TEXT_XL_PX,
    }

    _RADIUS_MAP: ClassVar[dict[str, int]] = {
        RadiusId.SM: dm.RADIUS_SM_PX,
        RadiusId.MD: dm.RADIUS_MD_PX,
        RadiusId.LG: dm.RADIUS_LG_PX,
        RadiusId.XL: dm.RADIUS_XL_PX,
    }

    _ICON_MAP: ClassVar[dict[str, int]] = {
        IconSizeId.XS: dm.ICON_XS_PX,
        IconSizeId.SM: dm.ICON_SM_PX,
        IconSizeId.MD: dm.ICON_MD_PX,
        IconSizeId.LG: dm.ICON_LG_PX,
    }

    def space_px(self, canonical: str) -> int:
        if canonical not in self._SPACE_MAP:
            raise KeyError(f"Unknown space token: {canonical}")
        return self._SPACE_MAP[canonical]

    def text_size_px(self, canonical: str) -> int:
        if canonical not in self._TEXT_MAP:
            raise KeyError(f"Unknown text.size token: {canonical}")
        return self._TEXT_MAP[canonical]

    def radius_px(self, canonical: str) -> int:
        if canonical not in self._RADIUS_MAP:
            raise KeyError(f"Unknown radius token: {canonical}")
        return self._RADIUS_MAP[canonical]

    def icon_size_px(self, canonical: str) -> int:
        if canonical not in self._ICON_MAP:
            raise KeyError(f"Unknown icon.size token: {canonical}")
        return self._ICON_MAP[canonical]

    def color(self, token: str) -> str:
        from app.gui.themes import get_theme_manager

        return get_theme_manager().color(token)

    def qss_token(self, canonical_color_token: str) -> str:
        """
        Resolved color string for a canonical ``color.*`` id, for Python-built QSS.
        """
        return self.color(canonical_color_token)

    @staticmethod
    def flat_name(canonical: str) -> str:
        """``text.size.sm`` → ``text_size_sm`` (for future QSS merge)."""
        return flat_key(canonical)


_registry: DesignTokenRegistry | None = None


def get_design_token_registry() -> DesignTokenRegistry:
    global _registry
    if _registry is None:
        _registry = DesignTokenRegistry()
    return _registry
