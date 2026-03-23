"""
Gruppierung kanonischer Farb-Tokens für den Theme-Visualizer.

Nur ThemeTokenId-Referenzen — keine Farbwerte.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.gui.themes.canonical_token_ids import ThemeTokenId


@dataclass(frozen=True)
class TokenGroup:
    title: str
    token_ids: tuple[str, ...]


TOKEN_GROUPS: tuple[TokenGroup, ...] = (
    TokenGroup(
        "Background",
        (
            ThemeTokenId.BG_APP,
            ThemeTokenId.BG_WINDOW,
            ThemeTokenId.BG_PANEL,
            ThemeTokenId.BG_SURFACE,
            ThemeTokenId.BG_SURFACE_ALT,
            ThemeTokenId.BG_SURFACE_ELEVATED,
            ThemeTokenId.BG_OVERLAY,
        ),
    ),
    TokenGroup(
        "Foreground",
        (
            ThemeTokenId.FG_PRIMARY,
            ThemeTokenId.FG_SECONDARY,
            ThemeTokenId.FG_MUTED,
            ThemeTokenId.FG_DISABLED,
            ThemeTokenId.FG_INVERSE,
            ThemeTokenId.FG_LINK,
        ),
    ),
    TokenGroup(
        "Border",
        (
            ThemeTokenId.BORDER_DEFAULT,
            ThemeTokenId.BORDER_SUBTLE,
            ThemeTokenId.BORDER_STRONG,
            ThemeTokenId.BORDER_FOCUS,
        ),
    ),
    TokenGroup(
        "Interaction",
        (
            ThemeTokenId.INTERACTION_HOVER,
            ThemeTokenId.INTERACTION_PRESSED,
            ThemeTokenId.INTERACTION_SELECTED,
            ThemeTokenId.INTERACTION_ACTIVE,
            ThemeTokenId.INTERACTION_FOCUS_RING,
            ThemeTokenId.SELECTION_BG,
            ThemeTokenId.SELECTION_FG,
        ),
    ),
    TokenGroup(
        "State",
        (
            ThemeTokenId.STATE_ACCENT,
            ThemeTokenId.STATE_ACCENT_HOVER,
            ThemeTokenId.STATE_ACCENT_PRESSED,
            ThemeTokenId.STATE_ACCENT_MUTED_BG,
            ThemeTokenId.STATE_SUCCESS,
            ThemeTokenId.STATE_WARNING,
            ThemeTokenId.STATE_ERROR,
            ThemeTokenId.STATE_INFO,
        ),
    ),
    TokenGroup(
        "Button",
        (
            ThemeTokenId.BUTTON_PRIMARY_BG,
            ThemeTokenId.BUTTON_PRIMARY_FG,
            ThemeTokenId.BUTTON_PRIMARY_HOVER,
            ThemeTokenId.BUTTON_PRIMARY_PRESSED,
            ThemeTokenId.BUTTON_SECONDARY_BG,
            ThemeTokenId.BUTTON_SECONDARY_FG,
            ThemeTokenId.BUTTON_SECONDARY_BORDER,
            ThemeTokenId.BUTTON_SECONDARY_HOVER,
            ThemeTokenId.BUTTON_DISABLED_BG,
            ThemeTokenId.BUTTON_DISABLED_FG,
        ),
    ),
    TokenGroup(
        "Input",
        (
            ThemeTokenId.INPUT_BG,
            ThemeTokenId.INPUT_FG,
            ThemeTokenId.INPUT_PLACEHOLDER,
            ThemeTokenId.INPUT_BORDER,
            ThemeTokenId.INPUT_BORDER_FOCUS,
            ThemeTokenId.INPUT_DISABLED_BG,
            ThemeTokenId.INPUT_DISABLED_FG,
        ),
    ),
    TokenGroup(
        "Navigation & Tabs",
        (
            ThemeTokenId.NAV_BG,
            ThemeTokenId.NAV_FG,
            ThemeTokenId.NAV_HOVER_BG,
            ThemeTokenId.NAV_ACTIVE_BG,
            ThemeTokenId.NAV_ACTIVE_FG,
            ThemeTokenId.TAB_BG,
            ThemeTokenId.TAB_FG,
            ThemeTokenId.TAB_ACTIVE_BG,
            ThemeTokenId.TAB_ACTIVE_FG,
            ThemeTokenId.TAB_INDICATOR,
        ),
    ),
    TokenGroup(
        "Table",
        (
            ThemeTokenId.TABLE_BG,
            ThemeTokenId.TABLE_FG,
            ThemeTokenId.TABLE_HEADER_BG,
            ThemeTokenId.TABLE_HEADER_FG,
            ThemeTokenId.TABLE_ROW_ALT_BG,
            ThemeTokenId.TABLE_GRID,
            ThemeTokenId.TABLE_SELECTION_BG,
            ThemeTokenId.TABLE_SELECTION_FG,
        ),
    ),
    TokenGroup(
        "Markdown",
        (
            ThemeTokenId.MARKDOWN_BODY,
            ThemeTokenId.MARKDOWN_HEADING,
            ThemeTokenId.MARKDOWN_LINK,
            ThemeTokenId.MARKDOWN_QUOTE,
            ThemeTokenId.MARKDOWN_QUOTE_BORDER,
            ThemeTokenId.MARKDOWN_INLINE_CODE_BG,
            ThemeTokenId.MARKDOWN_INLINE_CODE_FG,
            ThemeTokenId.MARKDOWN_CODEBLOCK_BG,
            ThemeTokenId.MARKDOWN_CODEBLOCK_FG,
            ThemeTokenId.MARKDOWN_TABLE_BORDER,
            ThemeTokenId.MARKDOWN_TABLE_HEADER_BG,
            ThemeTokenId.MARKDOWN_HR,
        ),
    ),
    TokenGroup(
        "Chat",
        (
            ThemeTokenId.CHAT_USER_BG,
            ThemeTokenId.CHAT_USER_FG,
            ThemeTokenId.CHAT_USER_BORDER,
            ThemeTokenId.CHAT_ASSISTANT_BG,
            ThemeTokenId.CHAT_ASSISTANT_FG,
            ThemeTokenId.CHAT_ASSISTANT_BORDER,
            ThemeTokenId.CHAT_SYSTEM_BG,
            ThemeTokenId.CHAT_SYSTEM_FG,
        ),
    ),
    TokenGroup(
        "Badge",
        (
            ThemeTokenId.BADGE_SUCCESS_BG,
            ThemeTokenId.BADGE_SUCCESS_FG,
            ThemeTokenId.BADGE_WARNING_BG,
            ThemeTokenId.BADGE_WARNING_FG,
            ThemeTokenId.BADGE_ERROR_BG,
            ThemeTokenId.BADGE_ERROR_FG,
            ThemeTokenId.BADGE_INFO_BG,
            ThemeTokenId.BADGE_INFO_FG,
        ),
    ),
    TokenGroup(
        "Menu & Tooltip",
        (
            ThemeTokenId.MENU_BG,
            ThemeTokenId.MENU_FG,
            ThemeTokenId.MENU_HOVER_BG,
            ThemeTokenId.TOOLTIP_BG,
            ThemeTokenId.TOOLTIP_FG,
        ),
    ),
    TokenGroup(
        "Domain (Monitoring / QA)",
        (
            ThemeTokenId.DOMAIN_MONITORING_BG,
            ThemeTokenId.DOMAIN_MONITORING_SURFACE,
            ThemeTokenId.DOMAIN_MONITORING_BORDER,
            ThemeTokenId.DOMAIN_MONITORING_TEXT,
            ThemeTokenId.DOMAIN_MONITORING_MUTED,
            ThemeTokenId.DOMAIN_MONITORING_ACCENT,
            ThemeTokenId.DOMAIN_MONITORING_ACCENT_BG,
            ThemeTokenId.DOMAIN_QA_NAV_SELECTED_BG,
            ThemeTokenId.DOMAIN_QA_NAV_SELECTED_FG,
        ),
    ),
)
