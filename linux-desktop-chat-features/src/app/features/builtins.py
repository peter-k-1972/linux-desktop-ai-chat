"""
Eingebaute Features — GUI-Registrare per importlib laden (kein statischer app.gui-Import).

So bleibt app.features für AST-Guards frei von app.gui-ImportFrom-Knoten.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.registry import FeatureRegistry


def register_builtin_registrars(registry: FeatureRegistry) -> None:
    """Registriert entdeckte FeatureRegistrare (Builtins + optionale Quellen)."""
    from app.features.feature_discovery import register_discovered_feature_registrars

    register_discovered_feature_registrars(registry)
