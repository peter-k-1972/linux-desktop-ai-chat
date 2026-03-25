"""
Edition-Auflösung und FeatureRegistry-Erzeugung für die gewählte Edition.

Kein Core-Import; kein GUI — nur app.features.* und lazy gui.registration über builtins.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from app.features.registry import FeatureRegistry

_LOG = logging.getLogger(__name__)

# Default: volle Desktop-Fläche (entspricht bisherigem Verhalten vor Edition-Bootstrap).
DEFAULT_DESKTOP_EDITION: str = "full"


def resolve_active_edition_name(cli_edition: Optional[str] = None) -> str:
    """
    Bestimmt die aktive Edition.

    Reihenfolge: CLI ``--edition`` / Namespace-Attribut, dann Umgebung ``LDC_EDITION``,
    sonst :data:`DEFAULT_DESKTOP_EDITION`.

    Unbekannte Namen: Warnung, dann nächste Quelle bzw. Default — kein Abbruch.
    """
    from app.features.editions.registry import build_default_edition_registry

    er = build_default_edition_registry()
    known = frozenset(er.list_editions())

    for raw in (cli_edition, os.environ.get("LDC_EDITION")):
        if raw is None or not str(raw).strip():
            continue
        key = str(raw).strip().lower()
        if key in known:
            return key
        _LOG.warning(
            "Unbekannte Edition %r (bekannt: %s) — nächste Quelle oder Default %r",
            raw,
            ", ".join(sorted(known)),
            DEFAULT_DESKTOP_EDITION,
        )
    return DEFAULT_DESKTOP_EDITION


def build_feature_registry_for_edition(edition_name: str) -> FeatureRegistry:
    """
    Registriert entdeckte Registrare, maskiert ``enabled`` nach ``effective_activation_features``.

    Builtins folgen der Edition wie bisher; **externe** Feature-Namen nur bei zusätzlicher
    Produktfreigabe (siehe ``feature_product_release`` / ``EditionDescriptor.released_plugin_features``).

    Unbekannte ``edition_name``: Fallback auf :data:`DEFAULT_DESKTOP_EDITION`.
    """
    from app.features.builtins import register_builtin_registrars
    from app.features.dependency_groups.registry import (
        build_default_dependency_group_registry,
        get_dependency_group_registry,
        set_dependency_group_registry,
    )
    from app.features.editions.registry import build_default_edition_registry
    from app.features.manifest_resolution import (
        effective_activation_features,
        effective_edition_features,
    )

    if get_dependency_group_registry() is None:
        set_dependency_group_registry(build_default_dependency_group_registry())

    er = build_default_edition_registry()
    ed = er.get_edition(edition_name)
    resolved = edition_name
    if ed is None:
        resolved = DEFAULT_DESKTOP_EDITION
        ed = er.get_edition(resolved)
        _LOG.warning("Edition %r nicht gefunden — nutze %r", edition_name, resolved)
    assert ed is not None
    declared = effective_edition_features(ed)
    activated = effective_activation_features(ed)
    blocked = declared - activated
    if blocked:
        _LOG.info(
            "Edition %r: externe Feature-Namen in der Edition, aber nicht produktfreigegeben — "
            "bleiben inaktiv: %s",
            resolved,
            ", ".join(sorted(blocked)),
        )
    reg = FeatureRegistry(edition_name=resolved)
    register_builtin_registrars(reg)
    reg.apply_active_feature_mask(activated)
    return reg
