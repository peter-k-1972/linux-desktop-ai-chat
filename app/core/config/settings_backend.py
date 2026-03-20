"""
SettingsBackend – Abstraktion für Einstellungsspeicher.

Qt-frei. Ermöglicht InMemoryBackend für Tests und QSettingsBackend für Produktion.
"""

from typing import Any, Protocol


class SettingsBackend(Protocol):
    """Protocol für Backend-Implementierungen (value/setValue wie QSettings)."""

    def value(self, key: str, default: Any = None) -> Any:
        """Liest einen Wert."""
        ...

    def setValue(self, key: str, value: Any) -> None:
        """Schreibt einen Wert."""
        ...


class InMemoryBackend:
    """In-Memory-Backend für Tests. Keine Persistenz, keine Qt-Abhängigkeit."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def value(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def setValue(self, key: str, value: Any) -> None:
        self._data[key] = value
