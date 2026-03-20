"""
ThemeTokens – zentrale Design-Tokens.

Farben, Typografie, Abstände, Radien, Borders.
Flache Struktur für QSS-Substitution.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ThemeTokens:
    """
    Design-Tokens für ein Theme.
    Flache Struktur: alle Werte als str für QSS.
    """

    # --- Colors: Background ---
    color_bg: str = "#f1f5f9"
    color_bg_surface: str = "#ffffff"
    color_bg_muted: str = "#f8fafc"
    color_bg_hover: str = "#e2e8f0"
    color_bg_selected: str = "#dbeafe"
    color_bg_input: str = "#ffffff"

    # --- Colors: Text ---
    color_text: str = "#1f2937"
    color_text_secondary: str = "#64748b"
    color_text_muted: str = "#94a3b8"
    color_text_inverse: str = "#ffffff"

    # --- Colors: Border ---
    color_border: str = "#e2e8f0"
    color_border_medium: str = "#cbd5e1"

    # --- Colors: Accent ---
    color_accent: str = "#1e40af"
    color_accent_hover: str = "#1d4ed8"
    color_accent_bg: str = "#dbeafe"

    # --- Colors: Status ---
    color_success: str = "#10b981"
    color_warning: str = "#f59e0b"
    color_error: str = "#ef4444"
    color_info: str = "#3b82f6"

    # --- Colors: Domain-spezifisch ---
    color_nav_bg: str = "#f8fafc"
    color_nav_selected_bg: str = "#dbeafe"
    color_nav_selected_fg: str = "#1e40af"
    color_monitoring_bg: str = "#0f172a"
    color_monitoring_surface: str = "#1e293b"
    color_monitoring_border: str = "#334155"
    color_monitoring_text: str = "#cbd5e1"
    color_monitoring_muted: str = "#64748b"
    color_monitoring_accent: str = "#34d399"
    color_monitoring_accent_bg: str = "#065f46"
    color_qa_nav_selected_bg: str = "#cffafe"
    color_qa_nav_selected_fg: str = "#0e7490"

    # --- Typography ---
    font_size_xs: str = "11px"
    font_size_sm: str = "12px"
    font_size_base: str = "13px"
    font_size_md: str = "14px"
    font_size_lg: str = "16px"
    font_size_xl: str = "20px"
    font_size_primary_title: str = "18px"
    font_size_section_title: str = "14px"
    font_size_panel_title: str = "13px"
    font_size_meta: str = "11px"
    font_weight_normal: str = "400"
    font_weight_medium: str = "500"
    font_weight_semibold: str = "600"
    font_weight_bold: str = "700"
    font_family_ui: str = "system-ui, sans-serif"
    font_family_mono: str = "monospace"

    # --- Spacing (Base: 4px) ---
    spacing_xs: str = "4px"
    spacing_sm: str = "8px"
    spacing_md: str = "12px"
    spacing_lg: str = "16px"
    spacing_xl: str = "24px"
    spacing_2xl: str = "32px"
    panel_padding: str = "20px"
    section_spacing: str = "24px"
    card_spacing: str = "16px"
    widget_spacing: str = "12px"
    nav_item_padding_v: str = "12px"
    nav_item_padding_h: str = "16px"

    # --- Radius ---
    radius_sm: str = "6px"
    radius_md: str = "8px"
    radius_lg: str = "10px"
    radius_xl: str = "12px"

    def to_dict(self) -> dict[str, str]:
        """Flaches Dict für QSS-Substitution."""
        return {
            k: v for k, v in self.__dict__.items()
            if isinstance(v, str)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThemeTokens":
        """Erstellt Tokens aus Dict (überschreibt nur angegebene Keys)."""
        defaults = cls().__dict__
        merged = {**defaults, **{k: str(v) for k, v in data.items() if k in defaults}}
        return cls(**merged)
