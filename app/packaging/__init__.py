"""
Repository-sichtbare Packaging-Landmarks.

Dieses Subpaket ist Teil der Host-Distribution ``linux-desktop-chat`` und markiert
kein separates pip-Paket. Es bündelt Konstanten für Dokumentation und leichte
Architektur-Guards.

Siehe: docs/architecture/PACKAGE_MAP.md
"""

from app.packaging.landmarks import (
    BRIDGE_APP_ROOT_MODULES,
    EXTENDED_APP_TOP_PACKAGES,
    PLUGIN_ENTRY_POINT_GROUP,
    REPO_LANDMARK_FILES,
)

__all__ = [
    "BRIDGE_APP_ROOT_MODULES",
    "EXTENDED_APP_TOP_PACKAGES",
    "PLUGIN_ENTRY_POINT_GROUP",
    "REPO_LANDMARK_FILES",
]
