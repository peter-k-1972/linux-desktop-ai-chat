"""
UICommandDispatcher — zentrales Routing von Commands zu Presentern.

Widgets sollen ``dispatch`` nutzen statt ``presenter.run(...)`` direkt aufzurufen.

Erwartung: registrierte Presenter implementieren ``run(command)`` (z. B.
:class:`app.ui_application.presenter_base.BasePresenter`).
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "UICommandDispatcher",
    "UnregisteredCommandError",
]


class UnregisteredCommandError(LookupError):
    """Kein Presenter für den konkreten Command-Typ registriert."""

    def __init__(self, command: object) -> None:
        self.command = command
        ct = type(command)
        super().__init__(f"no presenter registered for command type {ct!r}")


class UICommandDispatcher:
    """Mappt Command-Typen (``type(command)``) auf Presenter-Instanzen."""

    def __init__(self) -> None:
        self._by_command_type: dict[type[Any], Any] = {}

    def register(self, command_type: type[Any], presenter: Any) -> None:
        """Registriert einen Presenter für exakt diesen Command-Typ."""
        self._by_command_type[command_type] = presenter

    def dispatch(self, command: object) -> None:
        """Ruft ``presenter.run(command)`` für den zu ``type(command)`` passenden Presenter auf."""
        presenter = self._by_command_type.get(type(command))
        if presenter is None:
            raise UnregisteredCommandError(command)
        run = getattr(presenter, "run")
        run(command)
