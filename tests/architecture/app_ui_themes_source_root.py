"""
Pfad zum Quellbaum von ``app.ui_themes`` (Host-Workspace oder installiertes Wheel).

Nach Welle 7 liegt ``ui_themes`` nicht mehr unter ``APP_ROOT/ui_themes``;
Guards nutzen ``importlib.util.find_spec("app.ui_themes")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-ui-themes/src/app/ui_themes/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_ui_themes_source_root() -> Path:
    spec = importlib.util.find_spec("app.ui_themes")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.ui_themes nicht auffindbar — zuerst linux-desktop-chat-ui-themes "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-ui-themes"
        )
    return Path(spec.submodule_search_locations[0])
