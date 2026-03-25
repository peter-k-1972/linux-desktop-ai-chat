"""
Pfad zum Quellbaum von ``app.features`` (Host-Workspace oder installiertes Wheel).

Nach Commit 2 liegt die Feature-Plattform nicht mehr unter ``APP_ROOT/features``;
Guards und Tests nutzen ``importlib.util.find_spec("app.features")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-features/src/app/features/``.
**Nur Wheel:** ``…/site-packages/app/features`` — Segment-Guards laufen weiter, solange
das Paket installiert ist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_features_source_root() -> Path:
    spec = importlib.util.find_spec("app.features")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.features nicht auffindbar — zuerst linux-desktop-chat-features installieren, "
            "z. B.: python3 -m pip install -e ./linux-desktop-chat-features"
        )
    return Path(spec.submodule_search_locations[0])
