"""
Resolve :class:`SemanticPalette` + profile key → :class:`ThemeTokens` for QSS substitution.

QSS keeps existing ``color_*`` token names; semantic roles are the authoring layer only.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Literal

from app.gui.themes.semantic_palette import SemanticPalette
from app.gui.themes.tokens import ThemeTokens

ProfileKey = Literal["light_default", "dark_default", "workbench"]


def _domain_monitoring_qa(key: ProfileKey) -> dict[str, str]:
    """Runtime/debug/QA sidebars — tuned per chrome family."""
    if key == "light_default":
        return {
            "color_monitoring_bg": "#0f172a",
            "color_monitoring_surface": "#1e293b",
            "color_monitoring_border": "#334155",
            "color_monitoring_text": "#cbd5e1",
            "color_monitoring_muted": "#64748b",
            "color_monitoring_accent": "#34d399",
            "color_monitoring_accent_bg": "#065f46",
        }
    if key == "dark_default":
        return {
            "color_monitoring_bg": "#020617",
            "color_monitoring_surface": "#0f172a",
            "color_monitoring_border": "#334155",
            "color_monitoring_text": "#cbd5e1",
            "color_monitoring_muted": "#64748b",
            "color_monitoring_accent": "#34d399",
            "color_monitoring_accent_bg": "#065f46",
        }
    # workbench
    return {
        "color_monitoring_bg": "#020617",
        "color_monitoring_surface": "#0c1220",
        "color_monitoring_border": "#164e63",
        "color_monitoring_text": "#ccfbf1",
        "color_monitoring_muted": "#5eead4",
        "color_monitoring_accent": "#2dd4bf",
        "color_monitoring_accent_bg": "#134e4a",
    }


def semantic_palette_to_theme_tokens(profile_key: ProfileKey, palette: SemanticPalette) -> ThemeTokens:
    """Map semantic roles to flat ThemeTokens (colors + non-color defaults)."""
    base = ThemeTokens()
    color_map: dict[str, str] = {
        "color_bg": palette.bg_app,
        "color_nav_bg": palette.bg_panel,
        "color_bg_surface": palette.bg_surface,
        "color_bg_muted": palette.bg_surface_alt,
        "color_bg_elevated": palette.bg_elevated,
        "color_bg_hover": palette.bg_hover,
        "color_bg_selected": palette.bg_selected,
        "color_bg_input": palette.bg_input,
        "color_text": palette.fg_primary,
        "color_text_secondary": palette.fg_secondary,
        "color_text_muted": palette.fg_muted,
        "color_text_disabled": palette.fg_disabled,
        "color_text_inverse": palette.fg_on_accent,
        "color_fg_on_selected": palette.fg_on_selected,
        "color_border": palette.border_subtle,
        "color_border_medium": palette.border_default,
        "color_border_strong": palette.border_strong,
        "color_accent": palette.accent_primary,
        "color_accent_hover": palette.accent_hover,
        "color_accent_bg": palette.accent_muted_bg,
        "color_nav_selected_bg": palette.bg_selected,
        "color_nav_selected_fg": palette.fg_on_selected,
        "color_success": palette.status_success,
        "color_warning": palette.status_warning,
        "color_error": palette.status_error,
        "color_info": palette.status_info,
        "color_focus_ring": palette.focus_ring,
        "color_console_info": palette.console_info,
        "color_console_warning": palette.console_warning,
        "color_console_error": palette.console_error,
        "color_console_success": palette.console_success,
    }
    color_map.update(_domain_monitoring_qa(profile_key))
    # Single selection channel: QA Governance nav matches global chrome (not a third accent).
    color_map["color_qa_nav_selected_bg"] = color_map["color_nav_selected_bg"]
    color_map["color_qa_nav_selected_fg"] = color_map["color_nav_selected_fg"]
    return replace(base, **color_map)


def merge_semantic_aliases_for_qss(tokens: ThemeTokens) -> dict[str, str]:
    """
    Flat dict for loader: ThemeTokens.to_dict() plus optional semantic aliases.

    Aliases let QSS migrate gradually to role names identical to semantic fields.
    """
    d = tokens.to_dict()
    # Aliases = same values as resolved color_* (single source via ThemeTokens fields)
    d.setdefault("fg_primary", d.get("color_text", ""))
    d.setdefault("fg_secondary", d.get("color_text_secondary", ""))
    d.setdefault("fg_muted", d.get("color_text_muted", ""))
    d.setdefault("bg_app", d.get("color_bg", ""))
    d.setdefault("bg_panel", d.get("color_nav_bg", ""))
    d.setdefault("bg_surface", d.get("color_bg_surface", ""))
    d.setdefault("border_subtle", d.get("color_border", ""))
    d.setdefault("border_default", d.get("color_border_medium", ""))
    d.setdefault("border_strong", d.get("color_border_strong", ""))
    return d
