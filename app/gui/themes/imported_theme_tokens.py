"""
Abbildung importierter Theme-JSON (colors/fonts/metrics) auf :class:`ThemeTokens`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.tokens import ThemeTokens

# Kanonische Keys aus dem Benutzer-JSON → ThemeTokens-Felder
_COLOR_ALIASES: dict[str, str] = {
    "background": "color_bg",
    "panel": "color_bg_surface",
    "text": "color_text",
    "accent": "color_accent",
    "danger": "color_error",
}


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower().strip())
    return (s.strip("_") or "theme")[:80]


def build_theme_id_from_name(name: str, reserved: set[str]) -> str:
    """Erzeugt ``user_<slug>`` mit numerischem Suffix bei Kollision."""
    base = f"user_{_slugify(name)}"
    if base not in reserved:
        return base
    n = 2
    while f"{base}_{n}" in reserved:
        n += 1
    return f"{base}_{n}"


def theme_dict_to_token_updates(theme_dict: dict[str, Any]) -> dict[str, str]:
    """Wandelt importiertes JSON in ein für :meth:`ThemeTokens.from_dict` nutzbares Dict."""
    updates: dict[str, str] = {}
    colors = theme_dict.get("colors") or {}
    if isinstance(colors, dict):
        for k, v in colors.items():
            if not isinstance(k, str) or not isinstance(v, str):
                continue
            key = _COLOR_ALIASES.get(k, k)
            if key in ThemeTokens.__dataclass_fields__:
                updates[key] = v.strip()

    fonts = theme_dict.get("fonts") or {}
    if isinstance(fonts, dict):
        fam = fonts.get("default")
        if isinstance(fam, str) and fam.strip():
            updates["font_family_ui"] = f'"{fam.strip()}", sans-serif'
        size = fonts.get("size")
        if isinstance(size, (int, float)):
            updates["font_size_base"] = f"{int(size)}px"
        elif isinstance(size, str) and size.strip().isdigit():
            updates["font_size_base"] = f"{int(size)}px"

    metrics = theme_dict.get("metrics") or {}
    if isinstance(metrics, dict):
        r = metrics.get("radius")
        if isinstance(r, (int, float)):
            px = f"{int(r)}px"
            updates["radius_sm"] = px
            updates["radius_md"] = px
        sp = metrics.get("spacing")
        if isinstance(sp, (int, float)):
            updates["spacing_sm"] = f"{int(sp)}px"

    return updates


def theme_definition_from_import(
    theme_id: str,
    theme_dict: dict[str, Any],
    source_path: Path | None,
) -> ThemeDefinition:
    """Erzeugt :class:`ThemeDefinition` aus validiertem Import-JSON."""
    name = str(theme_dict.get("name", "")).strip() or theme_id
    token_updates = theme_dict_to_token_updates(theme_dict)
    tokens = ThemeTokens.from_dict(token_updates)
    return ThemeDefinition(
        id=theme_id,
        name=name,
        tokens=tokens,
        extends=None,
        _path=source_path,
    )
