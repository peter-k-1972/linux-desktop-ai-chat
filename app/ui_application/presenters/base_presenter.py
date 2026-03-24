"""
Gemeinsame Presenter-Basis — lebenszyklus und Hooks.

Presenter:
- nehmen Commands von der UI entgegen
- rufen Services / Ports auf
- wandeln Ergebnisse in Contract-State oder Patches um
- pushen über ChatUiSink (oder später andere Sinks)
"""

from __future__ import annotations

from typing import Optional


class BasePresenter:
    """Minimaler Lebenszyklus; konkrete Presenter erweitern."""

    def __init__(self) -> None:
        self._attached: bool = False

    def attach(self) -> None:
        """Abonnements starten (Timer, Bus, …) — Phase-1-Stub."""
        self._attached = True

    def detach(self) -> None:
        """Abonnements lösen — Phase-1-Stub."""
        self._attached = False

    @property
    def is_attached(self) -> bool:
        return self._attached

    def _require_sink(self, sink: Optional[object]) -> None:
        if sink is None:
            raise RuntimeError("Presenter requires a UI sink")
