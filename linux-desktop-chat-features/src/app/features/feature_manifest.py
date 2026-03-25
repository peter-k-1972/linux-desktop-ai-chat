"""
Feature-Manifest — Deskriptoren aus der Default-Registry (lazy, inkl. GUI-Registrare).

Statische Listen ohne GUI: app.features.descriptors + Tests mit Mock-Registraren bevorzugen.
"""

from __future__ import annotations

from app.features.descriptors import FeatureDescriptor

__all__ = ["FeatureDescriptor", "iter_default_feature_descriptors"]


def iter_default_feature_descriptors() -> tuple[FeatureDescriptor, ...]:
    """
    Alle eingebauten Feature-Deskriptore in Registry-Reihenfolge.

    Lädt GUI-Registrare (lazy über build_default_feature_registry).
    """
    from app.features.registry import build_default_feature_registry

    reg = build_default_feature_registry()
    return tuple(r.get_descriptor() for r in reg.list_registrars())
