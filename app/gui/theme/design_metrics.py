"""
Integer pixel metrics aligned with ``docs/design/DESIGN_TOKEN_DEFAULTS.md``.

QSS continues to use string values via ``ThemeTokens``; Python layouts and
``QSize`` should use these constants to avoid drift.
"""

from __future__ import annotations

# --- Spacing scale (4px grid + 2px micro) ---
SPACE_2XS_PX: int = 2
SPACE_XS_PX: int = 4
SPACE_SM_PX: int = 8
SPACE_MD_PX: int = 12
SPACE_LG_PX: int = 16
SPACE_XL_PX: int = 24
SPACE_2XL_PX: int = 32

# --- Semantic spacing ---
PANEL_PADDING_PX: int = 20
CARD_PADDING_PX: int = 16
DIALOG_PADDING_PX: int = 24
FORM_ROW_GAP_PX: int = 12
FORM_LABEL_GAP_PX: int = 8
# First column hint for desktop dialogs (apply via policy / future label sizing)
FORM_LABEL_MIN_WIDTH_DESKTOP_PX: int = 120
# Wide single-line fields (API keys, URLs)
WIDE_LINE_EDIT_MIN_WIDTH_PX: int = 280
# Gap between scroll content and button bar in modal dialogs
DIALOG_FOOTER_TOP_GAP_PX: int = 12
TOOLBAR_GAP_PX: int = 12
SIDEBAR_ITEM_GAP_PX: int = 4

# --- Typography (px) ---
TEXT_XS_PX: int = 11
TEXT_SM_PX: int = 12
TEXT_BASE_PX: int = 13
TEXT_MD_PX: int = 14
TEXT_LG_PX: int = 16
TEXT_XL_PX: int = 20
TEXT_PRIMARY_TITLE_PX: int = 18

# --- Radius ---
RADIUS_SM_PX: int = 6
RADIUS_MD_PX: int = 8
RADIUS_LG_PX: int = 10
RADIUS_XL_PX: int = 12

# --- Icon box (QSize / setIconSize) ---
ICON_XS_PX: int = 14
ICON_SM_PX: int = 16
ICON_MD_PX: int = 20
ICON_LG_PX: int = 24

# --- Control heights ---
INPUT_MD_HEIGHT_PX: int = 32
BUTTON_MD_MIN_HEIGHT_PX: int = 32
SIDEBAR_ITEM_MIN_HEIGHT_PX: int = 32
PANEL_HEADER_HEIGHT_PX: int = 40
DIALOG_MIN_WIDTH_PX: int = 480

# --- Compact padding presets (toolbar / chips) ---
PADDING_COMPACT_V_PX: int = 6
PADDING_COMPACT_H_PX: int = 12
PADDING_MICRO_V_PX: int = 4
PADDING_MICRO_H_PX: int = 8

# --- Header chrome profiles (L, T, R, B) — LAYOUT_SYSTEM_RULES ---
HEADER_STANDARD_MARGINS: tuple[int, int, int, int] = (12, 10, 12, 10)
HEADER_COMPACT_MARGINS: tuple[int, int, int, int] = (12, 8, 12, 8)
HEADER_ULTRA_MARGINS: tuple[int, int, int, int] = (8, 6, 8, 6)

# --- List rows (Operations / Explorer pattern) ---
LIST_ITEM_MIN_HEIGHT_PX: int = 32

# --- Chat (Operations / legacy ChatWidget) — siehe docs/design/CHAT_LAYOUT_POLICY.md ---
# Lesespalte: elastisch bis max; 800px im Korridor 720–960 (ruhige Zeilenlänge, 4px-Raster).
CHAT_CONTENT_MAX_WIDTH_PX: int = 800
# Bubble-Label (ConversationView / Legacy): etwas schmaler als Spalte → Innenrand bleibt sichtbar.
CHAT_BUBBLE_MAX_WIDTH_PX: int = 720
# Primäre Send-Aktion (Icon-Button oder „Senden“) — obere Grenze: prominente Aktion max. 40px.
CHAT_PRIMARY_SEND_HEIGHT_PX: int = 40
CHAT_PRIMARY_SEND_WIDTH_PX: int = 40
# Composer-Innen: Kartenrand; Zeilenabstand wie Form-Zwischenraum.
CHAT_COMPOSER_INNER_MARGINS_LTRB: tuple[int, int, int, int] = (
    CARD_PADDING_PX,
    SPACE_MD_PX,
    SPACE_MD_PX,
    SPACE_MD_PX,
)
CHAT_COMPOSER_WRAPPER_MARGINS_LTRB: tuple[int, int, int, int] = (
    PANEL_PADDING_PX,
    SPACE_LG_PX,
    PANEL_PADDING_PX,
    PANEL_PADDING_PX,
)
