"""
Basis-Typen für Screen-Registrare (Phase 1).

Später: gemeinsames Protokoll für feature-gesteuerte Registrierung.
"""

from __future__ import annotations

from typing import Callable, Protocol, Type, TypeVar

from PySide6.QtWidgets import QWidget

from app.gui.workspace.screen_registry import ScreenRegistry

W = TypeVar("W", bound=QWidget)


class RegistersScreens(Protocol):
    """Protokoll für Registrare, die Factories in die ScreenRegistry eintragen."""

    def register(self, registry: ScreenRegistry) -> None:
        ...


def make_screen_factory(screen_class: Type[W]) -> Callable[[], W]:
    """Erzeugt eine nullargumentige Factory für die ScreenRegistry."""

    def factory() -> W:
        return screen_class()

    return factory
