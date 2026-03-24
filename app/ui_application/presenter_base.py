"""
Wiederverwendbare Presenter-Pipeline: Command → Port → State → Sink.

Dieses Modul ergänzt :class:`app.ui_application.presenters.base_presenter.BasePresenter`
(Lebenszyklus) — bewusst separat, damit bestehende Presenter unverändert bleiben.

``operation`` ist entweder ein Callable ``(port, command) -> state`` oder der Name einer
Port-Methode, die genau ein Argument (das Command) erhält.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union


Operation = Union[str, Callable[[Any, Any], Any]]
ErrorStateFactory = Callable[[BaseException], Any]


class BasePresenter:
    """
    Führt eine Port-Operation aus und liefert den State an die Sink-Methode.

    Attribute ``command_type``, ``operation`` und ``sink_method`` sind nach ``__init__``
    gesetzt (Instanzattribute).
    """

    command_type: type[Any]
    operation: Operation
    sink_method: str

    def __init__(
        self,
        *,
        command_type: type[Any],
        operation: Operation,
        sink_method: str,
        port: Any,
        sink: Any,
        error_state_factory: ErrorStateFactory | None = None,
    ) -> None:
        self.command_type = command_type
        self.operation = operation
        self.sink_method = sink_method
        self._port = port
        self._sink = sink
        self._error_state_factory = error_state_factory

    def run(self, command: object) -> None:
        if not isinstance(command, self.command_type):
            raise TypeError(
                f"expected command type {self.command_type!r}, got {type(command)!r}",
            )
        try:
            state = self._invoke_port(command)
        except Exception as exc:
            if self._error_state_factory is None:
                raise
            state = self._error_state_factory(exc)
        sink_fn = getattr(self._sink, self.sink_method)
        sink_fn(state)

    def _invoke_port(self, command: Any) -> Any:
        op = self.operation
        if callable(op) and not isinstance(op, type):
            return op(self._port, command)
        if isinstance(op, str):
            fn = getattr(self._port, op)
            return fn(command)
        raise TypeError(f"operation must be callable or str, got {type(op)!r}")
