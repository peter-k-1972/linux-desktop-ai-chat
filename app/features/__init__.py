"""
Feature-Metadaten, Registry und FeatureRegistrar-Vertrag.

Phase 2: vertikale Aktivierung über FeatureRegistrar; Editionen folgen später.
"""

from app.features.builtins import register_builtin_registrars
from app.features.descriptors import FeatureDescriptor
from app.features.feature_manifest import iter_default_feature_descriptors
from app.features.feature_registry import (
    FeatureRegistry,
    apply_feature_screen_registrars,
    build_default_feature_registry,
    get_feature_registry,
    set_feature_registry,
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
    "get_dependency_group_registry",
    "get_edition_registry",
    "get_feature_registry",
    "iter_default_feature_descriptors",
    "resolve_active_edition_name",
    "register_builtin_registrars",
    "set_dependency_group_registry",
    "set_edition_registry",
    "set_feature_registry",
]
