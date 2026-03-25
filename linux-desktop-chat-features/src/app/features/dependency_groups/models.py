"""
DependencyGroupDescriptor — technische Install-/Extra-Gruppe, nicht Produktfeature.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DependencyGroupDescriptor:
    """
    Abbildet eine spätere pip-extra / Build-Slice-Gruppe.

    ``python_packages`` sind **informative** PyPI-Distributionsnamen (kein Installer hier).
    """

    name: str
    description: str
    python_packages: tuple[str, ...] = ()
    required_for_features: frozenset[str] = field(default_factory=frozenset)
    """Features, die diese Gruppe fachlich nahelegen (implizite Ableitung)."""
    optional: bool = False
    """True: Gruppe kann fehlen (fail-soft / reduced mode)."""
    platform_notes: str = ""
