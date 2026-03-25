"""
FeatureDescriptor — reine Metadaten, keine GUI/Qt.

Pakete liefern Code; Features beschreiben die vertikale Aktivierungseinheit.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureDescriptor:
    """
    Beschreibt ein logisches Feature (Produktschnitt), nicht die Python-Paketstruktur.

    ``screens`` / ``navigation_entries`` / ``commands`` sind informelle IDs
    (NavArea-Strings, Workspace-IDs, Command-IDs) für Doku, Guards und spätere Editionen.

    ``optional_dependencies`` sind Namen registrierter Dependency-Gruppen und steuern
    die technische Verfügbarkeit (``is_available()``) — siehe dependency_availability.
    """

    name: str
    description: str
    enabled_by_default: bool = True
    screens: tuple[str, ...] = ()
    navigation_entries: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    services: tuple[str, ...] = ()
    optional_dependencies: tuple[str, ...] = ()
    experimental: bool = False
    # Informative Zuordnung zu app/*-Top-Level-Paketen (keine Import-Anweisung)
    packages: tuple[str, ...] = ()
    # Top-Level-App-Pakete (z. B. core, gui), keine Feature-Namen — siehe FeatureCompatibility.requires_features.
    dependencies: tuple[str, ...] = ()
