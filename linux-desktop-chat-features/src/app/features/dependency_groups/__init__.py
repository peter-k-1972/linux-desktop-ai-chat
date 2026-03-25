"""Dependency-Group-Manifeste (technische Installationsgruppen)."""

from app.features.dependency_groups.models import DependencyGroupDescriptor
from app.features.dependency_groups.registry import (
    DependencyGroupRegistry,
    build_default_dependency_group_registry,
    get_dependency_group_registry,
    set_dependency_group_registry,
)

__all__ = [
    "DependencyGroupDescriptor",
    "DependencyGroupRegistry",
    "build_default_dependency_group_registry",
    "get_dependency_group_registry",
    "set_dependency_group_registry",
]
