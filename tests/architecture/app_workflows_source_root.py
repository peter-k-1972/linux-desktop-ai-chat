"""
Pfad zum Quellbaum von ``app.workflows`` (installiertes Wheel / editable).

Nach dem physischen Cut liegt ``workflows`` nicht mehr unter ``APP_ROOT/workflows``;
Guards nutzen ``importlib.util.find_spec("app.workflows")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-workflows/src/app/workflows/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_workflows_source_root() -> Path:
    spec = importlib.util.find_spec("app.workflows")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.workflows nicht auffindbar — zuerst linux-desktop-chat-workflows "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-workflows"
        )
    return Path(spec.submodule_search_locations[0])
