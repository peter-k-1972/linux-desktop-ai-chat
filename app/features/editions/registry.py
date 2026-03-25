"""
EditionRegistry — eingetragene EditionDescriptor, optional global für Bootstrap (später).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.features.editions.models import EditionDescriptor

_default_edition_registry: Optional["EditionRegistry"] = None


@dataclass
class EditionRegistry:
    _order: list[str] = field(default_factory=list)
    _editions: dict[str, EditionDescriptor] = field(default_factory=dict)

    def register_edition(self, edition: EditionDescriptor) -> None:
        if edition.name in self._editions:
            raise ValueError(f"Edition bereits registriert: {edition.name!r}")
        self._order.append(edition.name)
        self._editions[edition.name] = edition

    def get_edition(self, name: str) -> Optional[EditionDescriptor]:
        return self._editions.get(name)

    def list_editions(self) -> tuple[str, ...]:
        return tuple(self._order)

    def iter_editions(self) -> tuple[EditionDescriptor, ...]:
        return tuple(self._editions[n] for n in self._order)


def set_edition_registry(registry: Optional[EditionRegistry]) -> None:
    global _default_edition_registry
    _default_edition_registry = registry


def get_edition_registry() -> Optional[EditionRegistry]:
    return _default_edition_registry


def build_default_edition_registry() -> EditionRegistry:
    from app.features.editions.builtins import register_builtin_editions

    reg = EditionRegistry()
    register_builtin_editions(reg)
    return reg
