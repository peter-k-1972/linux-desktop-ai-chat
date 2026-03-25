"""
FeatureRegistrar — Vertrag für feature-gesteuerte Bootstrap-Beiträge.

Konkrete Implementierungen mit Qt/GUI: app.gui.registration.feature_builtins.

Kein Import von app.gui hier (AST-Guards / Paketgrenze).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.features.descriptors import FeatureDescriptor


@runtime_checkable
class FeatureRegistrar(Protocol):
    """
    Vertikale Einheit: ein Feature registriert seine Anteile am Shell-Bootstrap.

    ``screen_registry``: konkreter Typ app.gui.workspace.screen_registry.ScreenRegistry
    (hier als Any, um app.features von Qt/GUI fernzuhalten).

    Optional: ``get_feature_compatibility() -> FeatureCompatibility | None`` für Governance
    (siehe app.features.compatibility / feature_validation).
    """

    def get_descriptor(self) -> FeatureDescriptor:
        """Stabiler Name und Metadaten."""
        ...

    def register_screens(self, screen_registry: Any) -> None:
        """ScreenFactories in die globale ScreenRegistry eintragen."""
        ...

    def register_navigation(self, context: Any) -> None:
        """Phase 2: Platzhalter — zentraler Nav-Merge folgt."""
        ...

    def register_commands(self, context: Any) -> None:
        """Phase 2: Platzhalter — CommandRegistry bleibt vorerst zentral."""
        ...

    def register_services(self, context: Any) -> None:
        """Optional: Service-Wiring; Phase 2 typischerweise no-op."""
        ...

    def is_available(self) -> bool:
        """
        False z. B. bei fehlenden optionalen Extras — Registrierung wird übersprungen.

        Kein harter Abbruch der App; Aufrufer protokolliert best effort.
        """
        ...
