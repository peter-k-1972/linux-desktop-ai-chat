"""
Bootstrap – Registrierung aller Screens bei App-Start.

Phase 2: Screen-Registrierung läuft über FeatureRegistrar der FeatureRegistry.
Fallback ohne Registry: legacy register_all_navigation_area_screens.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from app.features import apply_feature_screen_registrars
from app.gui.registration.screen_registrar import register_all_navigation_area_screens
from app.gui.workspace.screen_registry import get_screen_registry

if TYPE_CHECKING:
    from app.features import FeatureRegistry

_LOG = logging.getLogger(__name__)


def register_all_screens(feature_registry: Optional["FeatureRegistry"] = None) -> None:
    """
    Registriert alle Screens in der ScreenRegistry.

    Konsumiert eingebaute FeatureRegistrare, wenn ``feature_registry`` gesetzt ist
    oder eine globale Registry via ``get_feature_registry()`` existiert.
    """
    from app.features import get_feature_registry

    registry = get_screen_registry()
    fr = feature_registry if feature_registry is not None else get_feature_registry()
    if fr is not None:
        n = apply_feature_screen_registrars(fr, registry)
        _LOG.debug("feature screen registrars applied: %s", n)
        return
    register_all_navigation_area_screens(registry)
