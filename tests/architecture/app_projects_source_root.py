"""
Pfad zum Quellbaum von ``app.projects`` (installiertes Wheel / editable).

Nach Commit 2 liegt ``projects`` nicht mehr unter ``APP_ROOT/projects``;
Guards nutzen ``importlib.util.find_spec("app.projects")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-projects/src/app/projects/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_projects_source_root() -> Path:
    spec = importlib.util.find_spec("app.projects")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.projects nicht auffindbar — zuerst linux-desktop-chat-projects "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-projects"
        )
    return Path(spec.submodule_search_locations[0])
