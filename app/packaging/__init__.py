"""
Repository-sichtbare Packaging-Landmarks.

Dieses Subpaket ist Teil der Host-Distribution ``linux-desktop-chat`` und markiert
kein separates pip-Paket. Es bündelt Konstanten für Dokumentation und leichte
Architektur-Guards.

Siehe: docs/architecture/PACKAGE_MAP.md
"""

from app.packaging.landmarks import (
    EXTENDED_APP_TOP_PACKAGES,
    PLUGIN_ENTRY_POINT_GROUP,
    REPO_LANDMARK_FILES,
    ROOT_APP_FILE_ROLES,
    ROOT_ROLE_CLASSIFIED_APP_ROOT_MODULES,
)

__all__ = [
    "EXTENDED_APP_TOP_PACKAGES",
    "PLUGIN_ENTRY_POINT_GROUP",
    "REPO_LANDMARK_FILES",
    "ROOT_APP_FILE_ROLES",
    "ROOT_ROLE_CLASSIFIED_APP_ROOT_MODULES",
]
