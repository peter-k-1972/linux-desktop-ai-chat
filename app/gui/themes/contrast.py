"""
WCAG-style contrast helpers for semantic palettes.

Used at build/test time to catch unreadable pairs; runtime theme apply does not fail hard.
"""

from __future__ import annotations

import re
from typing import Iterable


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Unsupported color: {hex_color!r}")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def _channel_luminance(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.x relative luminance in [0, 1]."""
    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * _channel_luminance(r) + 0.7152 * _channel_luminance(g) + 0.0722 * _channel_luminance(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Contrast ratio between two sRGB hex colors (>= 1)."""
    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_contrast_pairs(pairs: Iterable[tuple[str, str, str, float]]) -> list[str]:
    """
    pairs: (label, fg_hex, bg_hex, min_ratio).
    Returns human-readable violation messages (empty if OK).
    """
    errors: list[str] = []
    for label, fg, bg, minimum in pairs:
        try:
            r = contrast_ratio(fg, bg)
        except ValueError as e:
            errors.append(f"{label}: {e}")
            continue
        if r + 1e-6 < minimum:
            errors.append(f"{label}: contrast {r:.2f}:1 < required {minimum:.2f}:1 ({fg} on {bg})")
    return errors
