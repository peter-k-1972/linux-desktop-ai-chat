"""
Struktur- und Farbvalidierung für importierte Theme-JSON-Objekte.
"""

from __future__ import annotations

import re
from typing import Any

_HEX6 = re.compile(r"^#[0-9A-Fa-f]{6}$")


class ThemeValidationError(Exception):
    """Theme-Dict erfüllt nicht die Mindestanforderungen."""


def validate_theme(theme_dict: dict[str, Any]) -> None:
    """
    Prüft Pflichtfelder ``name`` und ``colors`` sowie Hex-Farben ``#RRGGBB``.

    :raises ThemeValidationError: bei Verstoß.
    """
    name = theme_dict.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ThemeValidationError('Pflichtfeld "name" fehlt oder ist leer.')

    colors = theme_dict.get("colors")
    if not isinstance(colors, dict) or not colors:
        raise ThemeValidationError('Pflichtfeld "colors" fehlt oder ist leer.')

    for key, val in colors.items():
        if not isinstance(key, str):
            raise ThemeValidationError("Farbschlüssel müssen Strings sein.")
        if not isinstance(val, str) or not _HEX6.fullmatch(val.strip()):
            raise ThemeValidationError(
                f'Farbe "{key}" muss ein Hex-String der Form #RRGGBB sein (ist: {val!r}).',
            )
