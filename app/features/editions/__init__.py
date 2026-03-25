"""Edition-Manifeste (deklarativ, ohne Laufzeit-Gating)."""

from app.features.editions.models import EditionDescriptor
from app.features.editions.registry import (
    EditionRegistry,
    build_default_edition_registry,
    get_edition_registry,
    set_edition_registry,
)

__all__ = [
    "EditionDescriptor",
    "EditionRegistry",
    "build_default_edition_registry",
    "get_edition_registry",
    "set_edition_registry",
]
