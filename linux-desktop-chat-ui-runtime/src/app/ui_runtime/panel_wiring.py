"""
Panel-Wiring — Adapter, Panel (als Sink) und Presenter zusammenführen.

Reduziert Boilerplate in Workspaces, ohne die Schichten Port/Adapter/Presenter zu ändern.

Konventionen (über Parameter steuerbar):

- **Adapter:** ``adapter_cls(**adapter_kwargs)`` (oder ``adapter_factory()`` wenn gesetzt).
- **Panel:** ``panel_cls(parent, **{port_kwarg: adapter}, **panel_kwargs)``.
- **Presenter:** Standard ``presenter_cls(panel, adapter)`` (Sink zuerst, Port zweites Argument —
  wie ``PromptStudioListPresenter`` / ``AgentTasksRegistryPresenter``), oder ``presenter_factory``.
- **Binden:** ``getattr(panel, bind_method)(presenter)``, sofern ``bind_method`` nicht ``None``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

__all__ = [
    "PresenterBinding",
    "wire_panel",
    "wire_panel_with_presenters",
]

P = TypeVar("P")


@dataclass(frozen=True, slots=True)
class PresenterBinding:
    """Eintrag für :func:`wire_panel_with_presenters`."""

    presenter_cls: type
    bind_method: str = "bind_presenter"
    factory: Callable[[Any, Any], Any] | None = None


def wire_panel(
    panel_cls: type[P],
    adapter_cls: type[Any] | Callable[..., Any],
    presenter_cls: type,
    *,
    parent: Any | None = None,
    port_kwarg: str = "port",
    adapter_kwargs: Mapping[str, Any] | None = None,
    panel_kwargs: Mapping[str, Any] | None = None,
    adapter_factory: Callable[[], Any] | None = None,
    presenter_factory: Callable[[Any, Any], Any] | None = None,
    bind_method: str | None = "bind_presenter",
) -> P:
    """
    Erzeugt Adapter → Panel (mit Port) → Presenter → optional ``panel.bind_*(presenter)``.

    Gibt das Panel zurück (Presenter hängt am Panel, sofern gebunden).
    """
    adapter = _make_adapter(adapter_cls, adapter_factory, adapter_kwargs)
    p_kwargs = dict(panel_kwargs or {})
    p_kwargs[port_kwarg] = adapter
    panel = panel_cls(parent, **p_kwargs)
    presenter = (
        presenter_factory(panel, adapter)
        if presenter_factory is not None
        else presenter_cls(panel, adapter)
    )
    if bind_method is not None:
        getattr(panel, bind_method)(presenter)
    return panel


def wire_panel_with_presenters(
    panel_cls: type[P],
    adapter_cls: type[Any] | Callable[..., Any],
    bindings: Sequence[PresenterBinding],
    *,
    parent: Any | None = None,
    port_kwarg: str = "port",
    adapter_kwargs: Mapping[str, Any] | None = None,
    panel_kwargs: Mapping[str, Any] | None = None,
    adapter_factory: Callable[[], Any] | None = None,
) -> P:
    """Wie :func:`wire_panel`, aber mehrere Presenter nacheinander an das Panel binden."""
    adapter = _make_adapter(adapter_cls, adapter_factory, adapter_kwargs)
    p_kwargs = dict(panel_kwargs or {})
    p_kwargs[port_kwarg] = adapter
    panel = panel_cls(parent, **p_kwargs)
    for spec in bindings:
        presenter = (
            spec.factory(panel, adapter)
            if spec.factory is not None
            else spec.presenter_cls(panel, adapter)
        )
        getattr(panel, spec.bind_method)(presenter)
    return panel


def _make_adapter(
    adapter_cls: type[Any] | Callable[..., Any],
    adapter_factory: Callable[[], Any] | None,
    adapter_kwargs: Mapping[str, Any] | None,
) -> Any:
    if adapter_factory is not None:
        return adapter_factory()
    kwargs = dict(adapter_kwargs or {})
    return adapter_cls(**kwargs)
