"""
Semantic color roles — single source of truth for theme profiles.

All built-in themes (light, dark, workbench) fill the same fields; QSS resolves via
:func:`palette_resolve.semantic_palette_to_theme_tokens`.
"""

from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(frozen=True, slots=True)
class SemanticPalette:
    """
    Theme-wide semantic colors. Naming is stable API for profiles and tests.

    Background / foreground pairs are validated in :mod:`app.gui.themes.contrast`.
    """

    # --- Backgrounds ---
    bg_app: str
    bg_panel: str
    bg_surface: str
    bg_surface_alt: str
    bg_elevated: str
    bg_input: str
    bg_hover: str
    bg_selected: str
    bg_disabled: str

    # --- Foregrounds ---
    fg_primary: str
    fg_secondary: str
    fg_muted: str
    fg_disabled: str
    fg_on_accent: str
    fg_on_success: str
    fg_on_warning: str
    fg_on_error: str
    fg_on_selected: str

    # --- Borders ---
    border_subtle: str
    border_default: str
    border_strong: str

    # --- Accent ---
    accent_primary: str
    accent_hover: str
    accent_active: str
    accent_muted_bg: str

    # --- Status (fills / indicators) ---
    status_success: str
    status_warning: str
    status_error: str
    status_info: str

    # --- Chrome extras ---
    shadow_color: str
    focus_ring: str
    console_info: str
    console_warning: str
    console_error: str
    console_success: str


def semantic_palette_field_names() -> frozenset[str]:
    """All semantic role keys (completeness checks)."""
    return frozenset(f.name for f in fields(SemanticPalette))
