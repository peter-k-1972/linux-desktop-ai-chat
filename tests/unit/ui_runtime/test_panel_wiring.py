"""app.ui_runtime.panel_wiring — Adapter / Panel / Presenter."""

from __future__ import annotations

from app.ui_runtime.panel_wiring import (
    PresenterBinding,
    wire_panel,
    wire_panel_with_presenters,
)


class _Adapter:
    def __init__(self, token: str = "a") -> None:
        self.token = token


class _Panel:
    def __init__(self, parent=None, *, port: _Adapter | None = None, extra: int = 0) -> None:
        del parent
        self.port = port
        self.extra = extra
        self.bound: list[object] = []

    def bind_presenter(self, presenter: object) -> None:
        self.bound.append(presenter)


class _Presenter:
    def __init__(self, sink: _Panel, port: _Adapter) -> None:
        self.sink = sink
        self.port = port


def test_wire_panel_creates_adapter_panel_presenter_and_binds() -> None:
    p = wire_panel(_Panel, _Adapter, _Presenter, parent=None, port_kwarg="port")
    assert isinstance(p, _Panel)
    assert isinstance(p.port, _Adapter)
    assert len(p.bound) == 1
    assert isinstance(p.bound[0], _Presenter)
    assert p.bound[0].sink is p
    assert p.bound[0].port is p.port


def test_wire_panel_passes_adapter_and_panel_kwargs() -> None:
    p = wire_panel(
        _Panel,
        _Adapter,
        _Presenter,
        adapter_kwargs={"token": "x"},
        panel_kwargs={"extra": 7},
    )
    assert p.port.token == "x"
    assert p.extra == 7


def test_wire_panel_custom_factory_and_bind_optional() -> None:
    created: list[str] = []

    def factory() -> _Adapter:
        created.append("a")
        return _Adapter("f")

    p = wire_panel(
        _Panel,
        _Adapter,
        _Presenter,
        adapter_factory=factory,
        bind_method=None,
    )
    assert created == ["a"]
    assert p.bound == []


def test_wire_panel_with_presenters_multiple_bindings() -> None:
    class _P2(_Presenter):
        pass

    class _PanelMulti(_Panel):
        def bind_beta(self, presenter: object) -> None:
            self.bound.append(presenter)

    p = wire_panel_with_presenters(
        _PanelMulti,
        _Adapter,
        (
            PresenterBinding(_Presenter, "bind_presenter"),
            PresenterBinding(_P2, "bind_beta"),
        ),
    )
    assert len(p.bound) == 2
    assert isinstance(p.bound[0], _Presenter)
    assert isinstance(p.bound[1], _P2)
