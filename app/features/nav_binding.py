"""
Ableitung sichtbarer Navigation und GUI-Nav-Commands aus der FeatureRegistry.

Liegt in ``app.features`` (kein app.gui-Import). Konsumenten: gui.navigation, gui.commands.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.registry import FeatureRegistry

_LOG = logging.getLogger(__name__)


def collect_active_navigation_entry_ids(feature_registry: FeatureRegistry) -> frozenset[str]:
    """
    Union von ``FeatureDescriptor.navigation_entries`` für enabled + ``is_available()`` Registrare.

    Enabled aber unavailable: kein Eintrag (fail-soft), optional Warnung.
    """
    ids: set[str] = set()
    for name in feature_registry.list_registrar_names():
        if not feature_registry.is_registrar_enabled(name):
            continue
        reg = feature_registry.get_registrar(name)
        if reg is None:
            continue
        desc = reg.get_descriptor()
        if not reg.is_available():
            if desc.navigation_entries:
                _LOG.warning(
                    "Feature %r: laut Edition aktiv, Registrar unavailable — Navigationseinträge übersprungen",
                    desc.name,
                )
            continue
        ids.update(desc.navigation_entries)
    return frozenset(ids)


def collect_active_gui_command_ids(feature_registry: FeatureRegistry) -> frozenset[str]:
    """Union von ``FeatureDescriptor.commands`` für enabled + available Registrare."""
    ids: set[str] = set()
    for name in feature_registry.list_registrar_names():
        if not feature_registry.is_registrar_enabled(name):
            continue
        reg = feature_registry.get_registrar(name)
        if reg is None:
            continue
        desc = reg.get_descriptor()
        if not reg.is_available():
            if desc.commands:
                _LOG.warning(
                    "Feature %r: laut Edition aktiv, Registrar unavailable — Nav-Commands übersprungen",
                    desc.name,
                )
            continue
        ids.update(desc.commands)
    return frozenset(ids)
