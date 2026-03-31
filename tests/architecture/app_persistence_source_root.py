"""
Pfad zum Quellbaum von ``app.persistence`` (installiertes Wheel / editable).

Nach dem physischen Cut liegt ``persistence`` nicht mehr unter ``APP_ROOT/persistence``;
Guards nutzen ``importlib.util.find_spec("app.persistence")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-persistence/src/app/persistence/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_persistence_source_root() -> Path:
    spec = importlib.util.find_spec("app.persistence")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.persistence nicht auffindbar — zuerst linux-desktop-chat-persistence "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-persistence "
            "oder den Host installieren: python3 -m pip install -e ."
        )
    return Path(spec.submodule_search_locations[0])
