"""app.ui_application.presenter_base — Command → Port → State → Sink."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.ui_application.presenter_base import BasePresenter


@dataclass
class _Cmd:
    value: int


@dataclass
class _State:
    ok: bool
    value: int = 0
    err: str | None = None


class _Sink:
    def __init__(self) -> None:
        self.states: list[_State] = []

    def push(self, state: _State) -> None:
        self.states.append(state)


def test_run_dispatches_correct_command_and_calls_port_and_sink() -> None:
    port_calls: list[tuple[int, ...]] = []

    class _Port:
        def load(self, cmd: _Cmd) -> _State:
            port_calls.append((cmd.value,))
            return _State(ok=True, value=cmd.value * 2)

    sink = _Sink()
    p = BasePresenter(
        command_type=_Cmd,
        operation="load",
        sink_method="push",
        port=_Port(),
        sink=sink,
    )
    p.run(_Cmd(3))
    assert port_calls == [(3,)]
    assert len(sink.states) == 1
    assert sink.states[0].ok is True
    assert sink.states[0].value == 6


def test_run_wrong_command_type_raises() -> None:
    p = BasePresenter(
        command_type=_Cmd,
        operation=lambda port, cmd: _State(ok=True),  # noqa: ARG005
        sink_method="push",
        port=object(),
        sink=_Sink(),
    )
    with pytest.raises(TypeError, match="expected command type"):
        p.run("not-a-command")  # type: ignore[arg-type]


def test_run_uses_callable_operation() -> None:
    class _Port:
        def x(self) -> None:
            pass

    def op(port: object, cmd: _Cmd) -> _State:
        del port
        return _State(ok=True, value=cmd.value)

    sink = _Sink()
    p = BasePresenter(
        command_type=_Cmd,
        operation=op,
        sink_method="push",
        port=_Port(),
        sink=sink,
    )
    p.run(_Cmd(5))
    assert sink.states[0].value == 5


def test_error_path_uses_factory_and_still_calls_sink() -> None:
    class _Port:
        def boom(self, cmd: _Cmd) -> _State:  # noqa: ARG002
            raise RuntimeError("svc down")

    sink = _Sink()

    def on_err(exc: BaseException) -> _State:
        return _State(ok=False, err=str(exc))

    p = BasePresenter(
        command_type=_Cmd,
        operation="boom",
        sink_method="push",
        port=_Port(),
        sink=sink,
        error_state_factory=on_err,
    )
    p.run(_Cmd(1))
    assert len(sink.states) == 1
    assert sink.states[0].ok is False
    assert "svc down" in (sink.states[0].err or "")


def test_error_without_factory_propagates_and_sink_not_called() -> None:
    class _Port:
        def boom(self, cmd: _Cmd) -> _State:  # noqa: ARG002
            raise ValueError("x")

    sink = _Sink()
    p = BasePresenter(
        command_type=_Cmd,
        operation="boom",
        sink_method="push",
        port=_Port(),
        sink=sink,
        error_state_factory=None,
    )
    with pytest.raises(ValueError, match="x"):
        p.run(_Cmd(0))
    assert sink.states == []
