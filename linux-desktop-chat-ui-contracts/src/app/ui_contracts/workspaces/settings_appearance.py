"""
Settings — Appearance / Theme (Qt-frei).

Commands, State und Patches für den ersten Settings-Migrationsschnitt.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Union

from app.ui_contracts.common.errors import SettingsErrorInfo

@dataclass(frozen=True, slots=True)
class ThemeListEntry:
    """Eine Zeile in der Theme-Liste."""

    theme_id: str
    display_name: str


@dataclass(frozen=True, slots=True)
class AppearanceSettingsState:
    """Vollzustand für die Theme-Auswahl."""

    themes: tuple[ThemeListEntry, ...]
    selected_theme_id: str
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class AppearanceStatePatch:
    """Teilupdate; None bei selected_theme_id = keine Änderung."""

    selected_theme_id: str | None = None
    error: SettingsErrorInfo | None = None
    has_error_update: bool = False


def merge_appearance_state(
    base: AppearanceSettingsState,
    patch: AppearanceStatePatch,
) -> AppearanceSettingsState:
    """Reiner Merge-Helfer für Presenter/Sink/Tests."""
    sid = patch.selected_theme_id if patch.selected_theme_id is not None else base.selected_theme_id
    err = patch.error if patch.has_error_update else base.error
    return replace(base, selected_theme_id=sid, error=err)


@dataclass(frozen=True, slots=True)
class LoadAppearanceSettingsCommand:
    """Theme-Liste und aktuelle Auswahl vom Port laden."""


@dataclass(frozen=True, slots=True)
class SelectThemeCommand:
    """Nutzer hat ein Theme aus der Liste gewählt."""

    theme_id: str


AppearanceCommand = Union[LoadAppearanceSettingsCommand, SelectThemeCommand]


class SettingsAppearancePortError(Exception):
    """
    Wird vom Port/Adapter bei Persistenz- oder Konsistenzfehlern geworfen.
    Presenter mappt auf SettingsErrorInfo.
    """

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
