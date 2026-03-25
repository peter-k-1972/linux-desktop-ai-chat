"""
Produktfreigabe für externe (discoverte) Plugin-Features.

Installation + Discovery + Governance reichen nicht: Aktivierung erfordert zusätzlich
einen Host-kontrollierten Freigabepfad (Allowlist + Edition).

Builtins (``ALL_BUILTIN_FEATURE_NAMES``) unterliegen **nicht** dieser Filterung.
"""

from __future__ import annotations

from app.features.editions.models import EditionDescriptor

#: Organisationsweite Freigabe ohne jede Edition einzeln pflegen zu müssen (meist leer).
CENTRAL_PRODUCT_RELEASED_PLUGIN_FEATURES: frozenset[str] = frozenset()


def product_releasable_plugin_feature_names(edition: EditionDescriptor) -> frozenset[str]:
    """
    Vereinigung zentraler und editionsbezogener Produktfreigabe für externe Namen,
    optional ergänzt/verengt durch YAML (``plugin_release_config``).
    """
    from app.features.plugin_release_config import apply_plugin_release_config

    code = CENTRAL_PRODUCT_RELEASED_PLUGIN_FEATURES | edition.released_plugin_features
    return apply_plugin_release_config(edition, code)
