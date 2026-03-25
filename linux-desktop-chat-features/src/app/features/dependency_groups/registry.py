"""
DependencyGroupRegistry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.features.dependency_groups.models import DependencyGroupDescriptor

_default_dep_registry: Optional["DependencyGroupRegistry"] = None


@dataclass
class DependencyGroupRegistry:
    _order: list[str] = field(default_factory=list)
    _groups: dict[str, DependencyGroupDescriptor] = field(default_factory=dict)

    def register_group(self, group: DependencyGroupDescriptor) -> None:
        if group.name in self._groups:
            raise ValueError(f"Dependency-Gruppe bereits registriert: {group.name!r}")
        self._order.append(group.name)
        self._groups[group.name] = group

    def get_group(self, name: str) -> Optional[DependencyGroupDescriptor]:
        return self._groups.get(name)

    def list_groups(self) -> tuple[str, ...]:
        return tuple(self._order)

    def iter_groups(self) -> tuple[DependencyGroupDescriptor, ...]:
        return tuple(self._groups[n] for n in self._order)


def set_dependency_group_registry(registry: Optional[DependencyGroupRegistry]) -> None:
    global _default_dep_registry
    _default_dep_registry = registry


def get_dependency_group_registry() -> Optional[DependencyGroupRegistry]:
    return _default_dep_registry


def build_default_dependency_group_registry() -> DependencyGroupRegistry:
    from app.features.dependency_groups.builtins import register_builtin_dependency_groups

    reg = DependencyGroupRegistry()
    register_builtin_dependency_groups(reg)
    return reg
