"""
Layout-Konstanten – einheitliche Abstände für die GUI.

Designsystem light: zentrale UI-Werte für Layouts.
Abgestimmt mit ThemeTokens (QSS). Base unit: 4px.

Verwendung:
    from app.gui.shared.layout_constants import (
        PANEL_PADDING,
        apply_panel_layout,
        apply_sidebar_layout,
    )
"""

from PySide6.QtWidgets import QLayout

# Base unit
BASE = 4

# Margins / Padding (px)
MARGIN_XS = 4
MARGIN_SM = 8
MARGIN_MD = 12
MARGIN_LG = 16
MARGIN_XL = 24
MARGIN_2XL = 32

# Content areas
PANEL_PADDING = 20
SECTION_SPACING = 24
CARD_SPACING = 16
WIDGET_SPACING = 12

# Screen / Workspace content
SCREEN_PADDING = 24
SCREEN_SPACING = 24
WORKSPACE_PADDING = 20
WORKSPACE_SPACING = 16

# Sidebar / Compact panels (Listen, Explorer)
SIDEBAR_PADDING = 12
SIDEBAR_SPACING = 10
HEADER_PADDING_V = 10
HEADER_PADDING_H = 12

# List items
LIST_ITEM_PADDING_V = 10
LIST_ITEM_PADDING_H = 12
LIST_ITEM_SPACING = 2

# Controls
CONTROL_HEIGHT = 32
BUTTON_PADDING_H = 12
BUTTON_PADDING_V = 8

# Toolbar / Content
TOOLBAR_CONTENT_GAP = 16

# Empty state / Info
EMPTY_STATE_PADDING = 24
EMPTY_STATE_PADDING_COMPACT = 16
EMPTY_STATE_PADDING_COMPACT_V = 24
EMPTY_STATE_SPACING = 12
EMPTY_STATE_SPACING_COMPACT = 6


def apply_panel_layout(
    layout: QLayout,
    *,
    padding: int | None = None,
    spacing: int | None = None,
) -> None:
    """
    Standard-Panel-Layout: einheitliche Margins und Spacing.

    Für Hauptinhaltsbereiche (z.B. Settings-Kategorien, Content).
    """
    p = padding if padding is not None else PANEL_PADDING
    s = spacing if spacing is not None else WIDGET_SPACING
    layout.setContentsMargins(p, p, p, p)
    layout.setSpacing(s)


def apply_sidebar_layout(
    layout: QLayout,
    *,
    padding: int | None = None,
    spacing: int | None = None,
) -> None:
    """
    Sidebar-Layout: kompakter für Listen, Explorer.

    Für Projekt-Header, Quellen-Listen, Prompt-Bibliothek.
    """
    p = padding if padding is not None else SIDEBAR_PADDING
    s = spacing if spacing is not None else SIDEBAR_SPACING
    layout.setContentsMargins(p, p, p, p)
    layout.setSpacing(s)


def apply_workspace_layout(
    layout: QLayout,
    *,
    padding: int | None = None,
    spacing: int | None = None,
) -> None:
    """
    Workspace-Layout: für zentrale Content-Bereiche.

    Für Prompt Studio Center, Agent Tasks, Knowledge Right.
    """
    p = padding if padding is not None else WORKSPACE_PADDING
    s = spacing if spacing is not None else WORKSPACE_SPACING
    layout.setContentsMargins(p, p, p, p)
    layout.setSpacing(s)


def apply_header_layout(layout: QLayout) -> None:
    """Header-Layout: für Sektionen mit Titel (z.B. Projekt-Header)."""
    layout.setContentsMargins(HEADER_PADDING_H, HEADER_PADDING_V, HEADER_PADDING_H, HEADER_PADDING_V)


def apply_settings_layout(layout: QLayout) -> None:
    """
    Settings-Kategorie-Layout: für Einstellungsseiten.

    Etwas mehr Luft als Standard-Panel (24px).
    """
    layout.setContentsMargins(SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING)
    layout.setSpacing(CARD_SPACING)
