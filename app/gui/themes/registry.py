"""
ThemeRegistry – Registrierung und Auflistung von Themes.

Built-in themes are authored as :class:`SemanticPalette` profiles, resolved to
:class:`ThemeTokens` for QSS (see :mod:`palette_resolve`).

Benutzer-Themes: JSON unter ``~/.linux_desktop_chat/themes/*.json``.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from app.gui.themes.builtin_semantic_profiles import (
    dark_semantic_profile,
    light_semantic_profile,
    workbench_semantic_profile,
)
from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.imported_theme_tokens import (
    build_theme_id_from_name,
    theme_definition_from_import,
)
from app.gui.themes.palette_resolve import semantic_palette_to_theme_tokens
from app.gui.themes.theme_loader import ThemeLoadError, load_theme_file
from app.gui.themes.theme_validator import ThemeValidationError, validate_theme

BUILTIN_THEME_IDS = frozenset({"light_default", "dark_default", "workbench"})


def user_themes_dir() -> Path:
    """Verzeichnis für installierte Benutzer-Themes."""
    return Path.home() / ".linux_desktop_chat" / "themes"


class ThemeRegistry:
    """
    Registry für verfügbare Themes.
    Lädt Built-ins fest; Benutzer-Themes aus ``user_themes_dir()``.
    """

    def __init__(self) -> None:
        self._themes: dict[str, ThemeDefinition] = {}
        self.reload_themes()

    def _load_builtin_themes(self) -> None:
        """Lädt die eingebauten Themes (light_default, dark_default, workbench)."""
        self._themes["light_default"] = _build_light_default()
        self._themes["dark_default"] = _build_dark_default()
        self._themes["workbench"] = _build_workbench()

    def _load_imported_themes(self) -> None:
        d = user_themes_dir()
        if not d.is_dir():
            return
        for path in sorted(d.glob("*.json")):
            theme_id = path.stem
            if theme_id in BUILTIN_THEME_IDS:
                continue
            try:
                data = load_theme_file(str(path))
                validate_theme(data)
            except (ThemeLoadError, ThemeValidationError):
                continue
            try:
                self._themes[theme_id] = theme_definition_from_import(theme_id, data, path)
            except Exception:
                continue

    def reload_themes(self) -> None:
        """Built-ins und Benutzer-Themes neu einlesen."""
        self._themes.clear()
        self._load_builtin_themes()
        self._load_imported_themes()

    def install_theme(self, path: str | Path) -> str:
        """
        Theme-JSON laden, validieren, nach ``user_themes_dir()`` kopieren, Registry neu laden.

        :returns: vergebene ``theme_id`` (Dateiname ohne ``.json``)
        """
        from app.gui.themes.theme_installer import ThemeInstallError

        src = Path(path).expanduser().resolve()
        if not src.is_file():
            raise ThemeInstallError(f"Datei nicht gefunden: {path}")

        try:
            data = load_theme_file(str(src))
            validate_theme(data)
        except ThemeLoadError as exc:
            raise ThemeInstallError(str(exc)) from exc
        except ThemeValidationError as exc:
            raise ThemeInstallError(str(exc)) from exc

        dest_dir = user_themes_dir()
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ThemeInstallError(f"Themen-Verzeichnis konnte nicht angelegt werden: {exc}") from exc

        reserved = set(self._themes.keys())
        for p in dest_dir.glob("*.json"):
            reserved.add(p.stem)
        theme_id = build_theme_id_from_name(str(data.get("name", "")), reserved)
        dest = dest_dir / f"{theme_id}.json"

        try:
            shutil.copy2(src, dest)
        except OSError as exc:
            raise ThemeInstallError(f"Theme konnte nicht kopiert werden: {exc}") from exc

        self.reload_themes()
        return theme_id

    def remove_theme(self, theme_id: str) -> None:
        """
        Entfernt ein Benutzer-Theme (Datei löschen, Registry neu laden).

        :raises ThemeInstallError: bei Built-in oder fehlender Datei
        """
        from app.gui.themes.theme_installer import ThemeInstallError

        if theme_id in BUILTIN_THEME_IDS:
            raise ThemeInstallError(f"Built-in-Theme kann nicht entfernt werden: {theme_id}")
        path = user_themes_dir() / f"{theme_id}.json"
        if not path.is_file():
            raise ThemeInstallError(f"Kein installiertes Theme: {theme_id}")
        try:
            path.unlink()
        except OSError as exc:
            raise ThemeInstallError(f"Theme-Datei konnte nicht gelöscht werden: {exc}") from exc
        self.reload_themes()

    def register(self, theme: ThemeDefinition) -> None:
        """Registriert ein Theme."""
        self._themes[theme.id] = theme

    def get(self, theme_id: str) -> ThemeDefinition | None:
        """Liefert ein Theme nach ID."""
        return self._themes.get(theme_id)

    def list_themes(self) -> list[tuple[str, str]]:
        """Liefert [(id, name), ...] aller registrierten Themes."""
        return [(t.id, t.name) for t in self._themes.values()]

    def __contains__(self, theme_id: str) -> bool:
        return theme_id in self._themes


def _build_light_default() -> ThemeDefinition:
    p = light_semantic_profile()
    return ThemeDefinition(
        id="light_default",
        name="Light",
        tokens=semantic_palette_to_theme_tokens("light_default", p),
        extends=None,
    )


def _build_dark_default() -> ThemeDefinition:
    p = dark_semantic_profile()
    return ThemeDefinition(
        id="dark_default",
        name="Dark",
        tokens=semantic_palette_to_theme_tokens("dark_default", p),
        extends=None,
    )


def _build_workbench() -> ThemeDefinition:
    p = workbench_semantic_profile()
    return ThemeDefinition(
        id="workbench",
        name="Workbench",
        tokens=semantic_palette_to_theme_tokens("workbench", p),
        extends=None,
    )
