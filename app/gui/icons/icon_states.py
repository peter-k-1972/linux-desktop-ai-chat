"""
Kanonische Icon-States und Zuordnung zu Theme-Tokens.

Siehe docs/design/ICON_STATE_MODEL.md, ICON_COLOR_RULES.md.
"""

from __future__ import annotations

from typing import Literal

from app.gui.themes.canonical_token_ids import ThemeTokenId

IconState = Literal[
    "default",
    "primary",
    "active",
    "selected",
    "disabled",
    "success",
    "warning",
    "error",
]

ICON_STATE_TO_TOKEN: dict[str, str] = {
    "default": ThemeTokenId.FG_SECONDARY,
    "primary": ThemeTokenId.FG_PRIMARY,
    "active": ThemeTokenId.STATE_ACCENT,
    "selected": ThemeTokenId.NAV_ACTIVE_FG,
    "disabled": ThemeTokenId.FG_DISABLED,
    "success": ThemeTokenId.STATE_SUCCESS,
    "warning": ThemeTokenId.STATE_WARNING,
    "error": ThemeTokenId.STATE_ERROR,
}

CANONICAL_ICON_STATES: frozenset[str] = frozenset(ICON_STATE_TO_TOKEN.keys())


def normalize_icon_state(state: str) -> str:
    s = (state or "default").strip().lower()
    return s if s in CANONICAL_ICON_STATES else "default"
