"""
Feature-Metadaten, Registry und FeatureRegistrar-Vertrag.

Phase 2: vertikale Aktivierung über FeatureRegistrar; Editionen folgen später.

Öffentliche Oberfläche für Host und externe Plugins: bevorzugt ``from app.features import …``
(siehe docs/architecture/PACKAGE_FEATURES_CUT_READY.md). CI darf zusätzlich
``app.features.release_matrix`` / ``app.features.dependency_packaging`` importieren.
"""

from app.features.builtins import register_builtin_registrars
from app.features.dependency_availability import is_feature_technically_available
from app.features.descriptors import FeatureDescriptor
from app.features.entry_point_contract import (
    ENTRY_POINT_GROUP,
    ENTRY_POINT_LEGACY_REGISTRARS_ATTR,
    ENTRY_POINT_PRIMARY_CALLABLE,
)
from app.features.feature_manifest import iter_default_feature_descriptors
from app.features.feature_registry import (
    FeatureRegistry,
    apply_feature_screen_registrars,
    build_default_feature_registry,
    get_feature_registry,
    set_feature_registry,
)
from app.features.nav_binding import (
    collect_active_gui_command_ids,
    collect_active_navigation_entry_ids,
)
from app.features.registrar import FeatureRegistrar

from app.features.edition_resolution import (
    DEFAULT_DESKTOP_EDITION,
    build_feature_registry_for_edition,
    resolve_active_edition_name,
)

# Edition / Dependency-Manifeste (deklarativ)
from app.features.dependency_groups import (
    DependencyGroupDescriptor,
    DependencyGroupRegistry,
    build_default_dependency_group_registry,
    get_dependency_group_registry,
    set_dependency_group_registry,
)
from app.features.editions import (
    EditionDescriptor,
    EditionRegistry,
    build_default_edition_registry,
    get_edition_registry,
    set_edition_registry,
)

__all__ = [
    "DEFAULT_DESKTOP_EDITION",
    "DependencyGroupDescriptor",
    "DependencyGroupRegistry",
    "ENTRY_POINT_GROUP",
    "ENTRY_POINT_LEGACY_REGISTRARS_ATTR",
    "ENTRY_POINT_PRIMARY_CALLABLE",
    "EditionDescriptor",
    "EditionRegistry",
    "FeatureDescriptor",
    "FeatureRegistrar",
    "FeatureRegistry",
    "apply_feature_screen_registrars",
    "build_default_dependency_group_registry",
    "build_default_edition_registry",
    "build_default_feature_registry",
    "build_feature_registry_for_edition",
    "collect_active_gui_command_ids",
    "collect_active_navigation_entry_ids",
    "get_dependency_group_registry",
    "get_edition_registry",
    "get_feature_registry",
    "is_feature_technically_available",
    "iter_default_feature_descriptors",
    "resolve_active_edition_name",
    "register_builtin_registrars",
    "set_dependency_group_registry",
    "set_edition_registry",
    "set_feature_registry",
]
