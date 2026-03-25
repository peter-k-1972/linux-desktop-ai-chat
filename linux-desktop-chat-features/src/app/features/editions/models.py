"""
EditionDescriptor — Produktzuschnitt als Feature-Menge (keine Paketliste).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EditionDescriptor:
    """
    Beschreibt eine Produktedition durch **Feature-Namen**, nicht durch Python-Pakete.

    Laufzeit-Gating ist bewusst noch nicht angebunden (Phase Manifest-only).
    """

    name: str
    description: str
    enabled_features: frozenset[str]
    """Explizit eingeschaltete Features (FeatureRegistrar-``name`` / Deskriptor-``name``)."""
    disabled_features: frozenset[str] = field(default_factory=frozenset)
    """Explizit ausgeschlossen (für Overrides / Dokumentation)."""
    released_plugin_features: frozenset[str] = field(default_factory=frozenset)
    """Produktfreigabe für **externe** Feature-Namen (nicht Builtin-Katalog).

    Nur Schnittmenge mit ``enabled_features`` kann nach Edition-Maske aktiv werden.
    Builtins sind immer „freigegeben“; dieses Feld betrifft Discovery-Features
    (Plugin / Extension / Entry Point / Env). Siehe ``feature_product_release`` /
    ``effective_activation_features``.
    """
    dependency_groups: tuple[str, ...] = ()
    """Namen technischer Dependency-Gruppen (siehe ``dependency_groups``-Registry)."""
    default_shell: str = "default_widget_gui"
    """gui_id / Shell-Alias für spätere Bootstrap-Auswahl."""
    experimental_allowed: bool = False
    visibility_profile: str = "public"
    """z. B. public | internal | partner — rein deklarativ."""
    notes: str = ""
    support_level: str = "community"
    """deklarativ; kein Support-Vertrag im Code."""
