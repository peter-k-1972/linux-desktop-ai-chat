"""app.ui_runtime.command_dispatcher — UICommandDispatcher."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.ui_runtime.command_dispatcher import UICommandDispatcher, UnregisteredCommandError


@dataclass
class _CmdA:
    x: int


@dataclass
class _CmdB:
    y: str


def test_dispatch_calls_presenter_run() -> None:
    calls: list[object] = []

    class _P:
        def run(self, command: object) -> None:
            calls.append(command)

    d = UICommandDispatcher()
    d.register(_CmdA, _P())
    d.dispatch(_CmdA(1))
    assert len(calls) == 1
    assert isinstance(calls[0], _CmdA)
    assert calls[0].x == 1


def test_dispatch_routes_to_correct_presenter() -> None:
    seen_a: list[int] = []
    seen_b: list[str] = []

    class _PA:
        def run(self, command: _CmdA) -> None:
            seen_a.append(command.x)

    class _PB:
        def run(self, command: _CmdB) -> None:
            seen_b.append(command.y)

    d = UICommandDispatcher()
    d.register(_CmdA, _PA())
    d.register(_CmdB, _PB())
    d.dispatch(_CmdB("hi"))
    d.dispatch(_CmdA(3))
    assert seen_a == [3]
    assert seen_b == ["hi"]


def test_dispatch_unregistered_raises() -> None:
    d = UICommandDispatcher()
    with pytest.raises(UnregisteredCommandError) as ei:
        d.dispatch(_CmdA(0))
    assert ei.value.command.x == 0


def test_multiple_presenters_independent() -> None:
    """Mehrere Command-Typen, jeweils eigener Presenter."""
    log: list[str] = []

    class _P1:
        def run(self, c: _CmdA) -> None:
            log.append(f"a{c.x}")

    class _P2:
        def run(self, c: _CmdB) -> None:
            log.append(f"b{c.y}")

    d = UICommandDispatcher()
    d.register(_CmdA, _P1())
    d.register(_CmdB, _P2())
    d.dispatch(_CmdA(9))
    d.dispatch(_CmdB("z"))
    assert log == ["a9", "bz"]
