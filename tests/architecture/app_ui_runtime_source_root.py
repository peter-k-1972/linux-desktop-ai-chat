"""
Pfad zum Quellbaum von ``app.ui_runtime`` (Host-Workspace oder installiertes Wheel).

Nach Welle 8 liegt ``ui_runtime`` nicht mehr unter ``APP_ROOT/ui_runtime``;
Guards nutzen ``importlib.util.find_spec("app.ui_runtime")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-ui-runtime/src/app/ui_runtime/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_ui_runtime_source_root() -> Path:
    spec = importlib.util.find_spec("app.ui_runtime")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.ui_runtime nicht auffindbar — zuerst linux-desktop-chat-ui-runtime "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-ui-runtime"
        )
    return Path(spec.submodule_search_locations[0])
