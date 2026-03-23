"""
Wiederverwendbare, token-basierte Styles für Control-Center-Panels.

Vermeidet Hardcoded Hex in providers_panels / models_panels / … (schrittweise Migration).
"""

from __future__ import annotations

from app.gui.themes.canonical_token_ids import ThemeTokenId
from app.gui.theme.design_metrics import (
    PADDING_COMPACT_H_PX,
    PADDING_COMPACT_V_PX,
    RADIUS_SM_PX,
    TEXT_SM_PX,
)


def _mgr_color(token: str) -> str:
    from app.gui.themes import get_theme_manager

    return get_theme_manager().color(token)


def cc_panel_frame_style() -> str:
    """
    Standard-Kartenrahmen für Control-Center.

    Kein QSS-Padding — Innenabstand kommt aus ``apply_card_inner_layout`` (16px),
    damit Python das kanonische Raster steuert (Pilot: Providers).
    """
    bg = _mgr_color(ThemeTokenId.BG_SURFACE)
    bd = _mgr_color(ThemeTokenId.BORDER_SUBTLE)
    return (
        f"background: {bg}; border: 1px solid {bd}; border-radius: 10px; "
        "padding: 0px;"
    )


def cc_section_title_style() -> str:
    fg = _mgr_color(ThemeTokenId.FG_SECONDARY)
    return f"font-weight: 600; font-size: 13px; color: {fg};"


def cc_muted_caption_style() -> str:
    fg = _mgr_color(ThemeTokenId.FG_MUTED)
    return f"color: {fg}; font-size: 11px;"


def cc_table_style() -> str:
    bg = _mgr_color(ThemeTokenId.TABLE_BG)
    grid = _mgr_color(ThemeTokenId.TABLE_GRID)
    return f"QTableWidget {{ background: {bg}; border: none; gridline-color: {grid}; }}"


def cc_refresh_button_style() -> str:
    """Sekundär-Akzent-Button (ehem. indigo Tailwind)."""
    bg = _mgr_color(ThemeTokenId.STATE_ACCENT_MUTED_BG)
    fg = _mgr_color(ThemeTokenId.STATE_ACCENT)
    hover = _mgr_color(ThemeTokenId.INTERACTION_HOVER)
    return (
        f"QPushButton {{ background: {bg}; color: {fg}; "
        f"padding: {PADDING_COMPACT_V_PX}px {PADDING_COMPACT_H_PX}px; "
        f"border-radius: {RADIUS_SM_PX}px; font-size: {TEXT_SM_PX}px; border: none; }} "
        f"QPushButton:hover {{ background: {hover}; }}"
    )


def cc_status_error_style() -> str:
    fg = _mgr_color(ThemeTokenId.STATE_ERROR)
    return f"color: {fg}; font-size: 11px;"


def cc_body_label_style() -> str:
    fg = _mgr_color(ThemeTokenId.FG_MUTED)
    return f"color: {fg}; font-size: 12px;"


def cc_name_emphasis_style() -> str:
    fg = _mgr_color(ThemeTokenId.FG_PRIMARY)
    return f"color: {fg}; font-size: 13px; font-weight: 500;"


def cc_online_badge_style() -> str:
    fg = _mgr_color(ThemeTokenId.STATE_SUCCESS)
    return f"color: {fg}; font-size: 12px; font-weight: 500;"


def cc_offline_badge_style() -> str:
    fg = _mgr_color(ThemeTokenId.STATE_ERROR)
    return f"color: {fg}; font-size: 12px;"
