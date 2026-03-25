"""
Abwärtskompatible Re-Exports der FeatureRegistry (Implementierung in registry.py).
"""

from app.features.edition_resolution import (
    DEFAULT_DESKTOP_EDITION,
    build_feature_registry_for_edition,
    resolve_active_edition_name,
)
from app.features.registry import (
    FeatureRegistry,
    apply_feature_screen_registrars,
    build_default_feature_registry,
    get_feature_registry,
    set_feature_registry,
)

__all__ = [
    "DEFAULT_DESKTOP_EDITION",
    "FeatureRegistry",
    "apply_feature_screen_registrars",
    "build_default_feature_registry",
    "build_feature_registry_for_edition",
    "get_feature_registry",
    "resolve_active_edition_name",
    "set_feature_registry",
]
