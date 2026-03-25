"""
Ableitungshilfen: Edition ↔ Features ↔ Dependency-Gruppen.

Keine Build- oder pip-Ausführung — nur Mengenlogik für spätere Automatisierung.
"""

from __future__ import annotations

from app.features.dependency_groups.registry import DependencyGroupRegistry
from app.features.editions.models import EditionDescriptor
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.feature_product_release import product_releasable_plugin_feature_names


def effective_edition_features(edition: EditionDescriptor) -> frozenset[str]:
    """Aktive Feature-Menge nach Abzug expliziter ``disabled_features``."""
    return frozenset(edition.enabled_features - edition.disabled_features)


def effective_activation_features(edition: EditionDescriptor) -> frozenset[str]:
    """
    Effektiv aktivierbare Feature-Namen für die Edition-Maske der Registry.

    - **Builtins** aus der Edition-Menge: wie bisher (keine Produktfreigabe nötig).
    - **Externe** Namen (nicht im Builtin-Katalog): nur wenn zusätzlich in der
      produktfreigegebenen Menge (Code + optional ``plugin_release_config``-YAML).

    Reihenfolge im Bootstrap: Discovery → Governance → Registry → Produktfreigabe (Code+Config) → **diese Menge** → Availability → UI.
    """
    declared = effective_edition_features(edition)
    builtins_active = declared & ALL_BUILTIN_FEATURE_NAMES
    external_declared = declared - ALL_BUILTIN_FEATURE_NAMES
    releasable = product_releasable_plugin_feature_names(edition)
    external_active = external_declared & releasable
    return frozenset(builtins_active | external_active)


def dependency_groups_implied_by_features(
    feature_names: frozenset[str],
    dep_registry: DependencyGroupRegistry,
) -> frozenset[str]:
    """
    Alle Gruppen, deren ``required_for_features`` die Feature-Menge schneidet.

    ``core`` schneidet immer, wenn alle Features in ``required_for_features`` liegen.
    """
    out: set[str] = set()
    for g in dep_registry.iter_groups():
        if g.required_for_features & feature_names:
            out.add(g.name)
    return frozenset(out)


def edition_declared_and_implied_dependency_groups(
    edition: EditionDescriptor,
    dep_registry: DependencyGroupRegistry,
) -> frozenset[str]:
    """Vereinigung explizit genannter Edition-Gruppen und feature-implizierter Gruppen."""
    eff = effective_edition_features(edition)
    implied = dependency_groups_implied_by_features(eff, dep_registry)
    return frozenset(edition.dependency_groups) | implied


def validate_edition_feature_references(
    edition: EditionDescriptor,
    known_features: frozenset[str],
) -> tuple[bool, tuple[str, ...]]:
    """
    Returns (ok, unknown_feature_names).

    Namen in ``known_features`` gelten als auflösbar (z. B. nach Discovery).
    Zusätzlich erlaubt: externe Namen, die explizit produktfreigegeben sind
    (zentral oder in ``edition.released_plugin_features``) — sie dürfen fehlen,
    wenn das Option-Paket nicht installiert ist.
    """
    releasable = product_releasable_plugin_feature_names(edition)
    unknown: set[str] = set()
    for f in edition.enabled_features | edition.disabled_features:
        if f in known_features:
            continue
        if f in releasable:
            continue
        unknown.add(f)
    return (not unknown, tuple(sorted(unknown)))


def validate_edition_dependency_group_references(
    edition: EditionDescriptor,
    known_groups: frozenset[str],
) -> tuple[bool, tuple[str, ...]]:
    unknown = [g for g in edition.dependency_groups if g not in known_groups]
    return (not unknown, tuple(unknown))


def validate_dependency_group_feature_references(
    _group_name: str,
    required_for_features: frozenset[str],
    known_features: frozenset[str],
) -> tuple[bool, tuple[str, ...]]:
    unknown = [f for f in required_for_features if f not in known_features]
    return (not unknown, tuple(unknown))
