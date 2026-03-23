"""
Built-in semantic color profiles: light, dark, workbench.

Neutral backgrounds/foregrounds/borders follow OKLCH H=250, C=0.01 (see docs/design/NEUTRAL_COLOR_SYSTEM.md).
Accent/status/console colors remain product defaults (teal / semantic).
"""

from __future__ import annotations

from app.gui.themes.semantic_palette import SemanticPalette


def light_semantic_profile() -> SemanticPalette:
    """Light chrome — OKLCH neutrals + Slate+Teal accent."""
    return SemanticPalette(
        # OKLCH ladder: mirrored bg order + explicit borders (edge-contrast tuned)
        bg_app="#b0b5ba",
        bg_panel="#c1c6cc",
        bg_surface="#d1d6dc",
        bg_surface_alt="#ccd2d7",
        bg_elevated="#d9dfe5",
        bg_input="#c6cbd1",
        bg_hover="#b7bdc2",
        bg_selected="#99f6e4",
        bg_disabled="#d3d8de",
        fg_primary="#000001",
        fg_secondary="#25292e",
        fg_muted="#4e5358",
        fg_disabled="#65696f",
        fg_on_accent="#ffffff",
        fg_on_success="#ffffff",
        fg_on_warning="#1c1917",
        fg_on_error="#ffffff",
        fg_on_selected="#134e4a",
        border_subtle="#a0a5ab",
        border_default="#888d92",
        border_strong="#44484d",
        accent_primary="#0f766e",
        accent_hover="#0d9488",
        accent_active="#115e59",
        accent_muted_bg="#ccfbf1",
        status_success="#059669",
        status_warning="#d97706",
        status_error="#dc2626",
        status_info="#0d9488",
        shadow_color="#0f172a33",
        focus_ring="#0d9488",
        console_info="#14b8a6",
        console_warning="#f59e0b",
        console_error="#ef4444",
        console_success="#10b981",
    )


def dark_semantic_profile() -> SemanticPalette:
    """Dark chrome — OKLCH neutrals + Slate+Teal accent."""
    return SemanticPalette(
        bg_app="#020306",
        bg_panel="#04070a",
        bg_surface="#0d1115",
        bg_surface_alt="#06090d",
        bg_elevated="#191d22",
        bg_input="#0a0e11",
        bg_hover="#14181c",
        bg_selected="#134e4a",
        bg_disabled="#040609",
        fg_primary="#edf2f8",
        fg_secondary="#a0a5ab",
        fg_muted="#70757a",
        fg_disabled="#595e63",
        fg_on_accent="#042f2e",
        fg_on_success="#052e16",
        fg_on_warning="#1c1917",
        fg_on_error="#ffffff",
        fg_on_selected="#ecfdf5",
        border_subtle="#25292e",
        border_default="#393e42",
        border_strong="#4e5358",
        accent_primary="#2dd4bf",
        accent_hover="#5eead4",
        accent_active="#14b8a6",
        accent_muted_bg="#115e59",
        status_success="#34d399",
        status_warning="#fbbf24",
        status_error="#f87171",
        status_info="#5eead4",
        shadow_color="#00000066",
        focus_ring="#2dd4bf",
        console_info="#5eead4",
        console_warning="#fcd34d",
        console_error="#fca5a5",
        console_success="#6ee7b7",
    )


def workbench_semantic_profile() -> SemanticPalette:
    """
    Workbench-first dark profile — deeper OKLCH neutral ladder + cyan accent.
    """
    return SemanticPalette(
        bg_app="#000101",
        bg_panel="#010102",
        bg_surface="#020406",
        bg_surface_alt="#010204",
        bg_elevated="#05080b",
        bg_input="#020305",
        bg_hover="#040609",
        bg_selected="#0e7490",
        bg_disabled="#000102",
        fg_primary="#edf2f8",
        fg_secondary="#a0a5ab",
        fg_muted="#70757a",
        fg_disabled="#595e63",
        fg_on_accent="#042f2e",
        fg_on_success="#022c22",
        fg_on_warning="#1c1917",
        fg_on_error="#ffffff",
        fg_on_selected="#ecfeff",
        border_subtle="#25292e",
        border_default="#34383d",
        border_strong="#494e52",
        accent_primary="#22d3ee",
        accent_hover="#67e8f9",
        accent_active="#06b6d4",
        accent_muted_bg="#164e63",
        status_success="#2dd4bf",
        status_warning="#fbbf24",
        status_error="#fb7185",
        status_info="#38bdf8",
        shadow_color="#00000088",
        focus_ring="#22d3ee",
        console_info="#7dd3fc",
        console_warning="#fcd34d",
        console_error="#fda4af",
        console_success="#5eead4",
    )
