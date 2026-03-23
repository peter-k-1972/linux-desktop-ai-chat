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

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLayout, QVBoxLayout

from app.gui.theme import design_metrics as _dm

HeaderProfile = Literal["standard", "compact", "ultra"]

# Base unit
BASE = 4

# --- Canonical aliases (numeric source: ``design_metrics``) ---
DIALOG_CONTENT_PADDING = _dm.DIALOG_PADDING_PX
CARD_INNER_PADDING = _dm.CARD_PADDING_PX

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
    apply_header_profile_margins(layout, "standard")


def apply_header_profile_margins(layout: QLayout, profile: HeaderProfile) -> None:
    """
    Workbench-/Operations-Header-Ränder (siehe ``design_metrics.HEADER_*_MARGINS``).

    - ``standard`` — PanelHeader, Explorer-Titelzeilen
    - ``compact`` — WorkflowCanvasHeader
    - ``ultra`` — ContextActionBar
    """
    if profile == "standard":
        l, t, r, b = _dm.HEADER_STANDARD_MARGINS
    elif profile == "compact":
        l, t, r, b = _dm.HEADER_COMPACT_MARGINS
    else:
        l, t, r, b = _dm.HEADER_ULTRA_MARGINS
    layout.setContentsMargins(l, t, r, b)


def apply_settings_layout(layout: QLayout) -> None:
    """
    Settings-Kategorie-Layout: für Einstellungsseiten.

    Etwas mehr Luft als Standard-Panel (24px).
    """
    layout.setContentsMargins(SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING)
    layout.setSpacing(CARD_SPACING)


def apply_dialog_scroll_content_layout(
    layout: QVBoxLayout,
    *,
    padding: int | None = None,
    section_spacing: int | None = None,
) -> None:
    """
    Innerer Inhalt eines modalen Dialogs mit ScrollArea.

    Padding = Dialog-Innenrand (24px). Vertikaler Abstand zwischen Hauptblöcken
    (Form, QGroupBox) = Card/Section-Gap (16px).
    """
    p = padding if padding is not None else _dm.DIALOG_PADDING_PX
    s = section_spacing if section_spacing is not None else CARD_SPACING
    layout.setContentsMargins(p, p, p, p)
    layout.setSpacing(s)


def apply_dialog_button_bar_layout(layout: QHBoxLayout) -> None:
    """Button-Leiste: horizontal bündig mit Dialog-Padding, Standard-Button-Abstand."""
    layout.setContentsMargins(_dm.DIALOG_PADDING_PX, 0, _dm.DIALOG_PADDING_PX, 0)
    layout.setSpacing(_dm.SPACE_MD_PX)


def apply_form_layout_policy(form: QFormLayout) -> None:
    """
    Kanonische Form-Policy für Desktop-Dialoge (siehe docs/design/LAYOUT_SYSTEM_RULES.md).

    - Zeilenabstand 12px, Label↔Feld 8px
    - Labels rechtsbündig (schmale erste Spalte)
    - Felder wachsen horizontal

    Mindestbreite der Label-Spalte (120px) ist als ``FORM_LABEL_MIN_WIDTH_DESKTOP_PX``
    in ``design_metrics`` dokumentiert; Qt setzt sie nicht automatisch — bei Bedarf
    pro Zeile an QLabel anwenden.
    """
    form.setVerticalSpacing(_dm.FORM_ROW_GAP_PX)
    form.setHorizontalSpacing(_dm.FORM_LABEL_GAP_PX)
    form.setLabelAlignment(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    form.setFieldGrowthPolicy(
        QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
    )


def apply_card_inner_layout(layout: QLayout) -> None:
    """Innenabstand für CC-/Karten-Panel-Inhalt (16px) — QSS-Frame ohne Zusatz-Padding."""
    p = _dm.CARD_PADDING_PX
    layout.setContentsMargins(p, p, p, p)
