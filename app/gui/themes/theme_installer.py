"""
Installation importierter Themes über die :class:`ThemeRegistry`.

Die eigentliche Logik liegt in :meth:`ThemeRegistry.install_theme`;
diese Klasse ist die öffentliche Fassade für die GUI (ohne direkten Registry-Zugriff).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.gui.themes.registry import ThemeRegistry


class ThemeInstallError(Exception):
    """Installation fehlgeschlagen (z. B. Zielpfad, Konflikt)."""


class ThemeInstaller:
    """Installiert eine Theme-JSON-Datei und lädt die Registry neu."""

    def __init__(self, registry: ThemeRegistry | None = None) -> None:
        self._registry = registry

    def install_theme(self, path: str) -> str:
        """
        Theme aus ``path`` installieren.

        :returns: neue ``theme_id``
        :raises ThemeLoadError: siehe :mod:`theme_loader`
        :raises ThemeValidationError: siehe :mod:`theme_validator`
        :raises ThemeInstallError: Kopieren oder ID-Vergabe
        """
        from app.gui.themes.manager import get_theme_manager

        reg = self._registry if self._registry is not None else get_theme_manager().registry
        return reg.install_theme(path)
