"""
ScreenRegistry – Zentrale Registrierung von area_id → Screen-Factory.

Keine If/Else-Ketten. Bereichsumschaltung über Registry.
"""

from typing import Callable
from PySide6.QtWidgets import QWidget


class ScreenRegistry:
    """Registry für Screens. area_id → Factory (Callable[[], QWidget])."""

    def __init__(self):
        self._factories: dict[str, Callable[[], QWidget]] = {}
        self._titles: dict[str, str] = {}

    def register(self, area_id: str, factory: Callable[[], QWidget], title: str = "") -> None:
        """Registriert einen Screen für area_id."""
        self._factories[area_id] = factory
        self._titles[area_id] = title or area_id.replace("_", " ").title()

    def get_factory(self, area_id: str) -> Callable[[], QWidget] | None:
        """Liefert die Factory für area_id oder None."""
        return self._factories.get(area_id)

    def get_title(self, area_id: str) -> str:
        """Liefert den Titel für area_id."""
        return self._titles.get(area_id, area_id)

    def create_screen(self, area_id: str) -> QWidget | None:
        """Erstellt eine Screen-Instanz für area_id."""
        factory = self.get_factory(area_id)
        if factory:
            return factory()
        return None

    def list_areas(self) -> list[str]:
        """Liefert alle registrierten area_ids."""
        return list(self._factories.keys())


# Singleton für App-weite Nutzung
_registry: ScreenRegistry | None = None


def get_screen_registry() -> ScreenRegistry:
    """Liefert die globale ScreenRegistry."""
    global _registry
    if _registry is None:
        _registry = ScreenRegistry()
    return _registry
