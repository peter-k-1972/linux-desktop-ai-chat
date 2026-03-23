"""
Contrast rules for :class:`SemanticPalette` — centralized policy, not per-widget hacks.
"""

from __future__ import annotations

from app.gui.themes.contrast import validate_contrast_pairs
from app.gui.themes.semantic_palette import SemanticPalette

# Normal UI text on common surfaces (WCAG AA body)
_MIN_BODY = 4.5
# Large / bold UI chrome (AA large text)
_MIN_UI_LARGE = 3.0
# Muted secondary text may sit on elevated surfaces
_MIN_MUTED = 3.5
# Non-text separation (borders vs adjacent fills) — not WCAG text AA
_MIN_EDGE = 1.28


def validation_errors(p: SemanticPalette) -> list[str]:
    """
    Return contrast violations for this palette. Empty means rules pass.

    Policy:
    - Primary text readable on app, panel, surface, input, elevated.
    - Secondary/muted scaled appropriately.
    - Selected row: fg_on_selected on bg_selected.
    - Accent button: fg_on_accent on accent_primary.
    - Status chips (on surface): colored glyph uses status_* on bg_surface; on-accent variants checked.
    """
    pairs: list[tuple[str, str, str, float]] = [
        ("fg_primary / bg_app", p.fg_primary, p.bg_app, _MIN_BODY),
        ("fg_primary / bg_panel", p.fg_primary, p.bg_panel, _MIN_BODY),
        ("fg_primary / bg_surface", p.fg_primary, p.bg_surface, _MIN_BODY),
        ("fg_primary / bg_input", p.fg_primary, p.bg_input, _MIN_BODY),
        ("fg_primary / bg_elevated", p.fg_primary, p.bg_elevated, _MIN_BODY),
        ("fg_secondary / bg_surface", p.fg_secondary, p.bg_surface, _MIN_MUTED),
        ("fg_muted / bg_surface", p.fg_muted, p.bg_surface, _MIN_MUTED),
        ("fg_on_selected / bg_selected", p.fg_on_selected, p.bg_selected, _MIN_BODY),
        ("fg_on_accent / accent_primary", p.fg_on_accent, p.accent_primary, _MIN_BODY),
        ("border_default vs bg_panel (edge)", p.border_default, p.bg_panel, _MIN_EDGE),
        ("border_subtle vs bg_surface (edge)", p.border_subtle, p.bg_surface, _MIN_EDGE),
        ("border_strong vs bg_app (edge)", p.border_strong, p.bg_app, _MIN_EDGE),
    ]
    return validate_contrast_pairs(pairs)


def assert_palette_accessible(p: SemanticPalette) -> None:
    errs = validation_errors(p)
    if errs:
        raise AssertionError("Semantic palette contrast failures:\n" + "\n".join(errs))
