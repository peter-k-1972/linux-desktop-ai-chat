"""
Canonical token id strings (documentation parity with ``docs/design/DESIGN_TOKEN_SPEC.md``).

Colors: use :class:`app.gui.themes.canonical_token_ids.ThemeTokenId` — not duplicated here.
"""

from __future__ import annotations


class SpaceId:
    """Non-color spacing canonical ids."""

    X2S = "space.2xs"
    XS = "space.xs"
    SM = "space.sm"
    MD = "space.md"
    LG = "space.lg"
    XL = "space.xl"
    X2L = "space.2xl"


class TextSizeId:
    XS = "text.size.xs"
    SM = "text.size.sm"
    BASE = "text.size.base"
    MD = "text.size.md"
    LG = "text.size.lg"
    XL = "text.size.xl"


class IconSizeId:
    XS = "icon.size.xs"
    SM = "icon.size.sm"
    MD = "icon.size.md"
    LG = "icon.size.lg"


class RadiusId:
    SM = "radius.sm"
    MD = "radius.md"
    LG = "radius.lg"
    XL = "radius.xl"
