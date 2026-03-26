"""
Pfad zum Quellbaum von ``app.utils`` (Host-Workspace oder installiertes Wheel).

Nach Welle 6 liegt ``utils`` nicht mehr unter ``APP_ROOT/utils``;
Guards nutzen ``importlib.util.find_spec("app.utils")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-utils/src/app/utils/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_utils_source_root() -> Path:
    spec = importlib.util.find_spec("app.utils")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.utils nicht auffindbar — zuerst linux-desktop-chat-utils "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-utils"
        )
    return Path(spec.submodule_search_locations[0])
