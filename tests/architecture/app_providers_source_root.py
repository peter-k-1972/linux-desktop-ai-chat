"""
Pfad zum Quellbaum von ``app.providers`` (Host-Workspace oder installiertes Wheel).

Nach Commit 2 liegt ``providers`` nicht mehr unter ``APP_ROOT/providers``;
Guards nutzen ``importlib.util.find_spec("app.providers")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-providers/src/app/providers/``.
**Nur Wheel:** ``…/site-packages/app/providers`` — Segment-Guards laufen weiter, solange
das Paket installiert ist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_providers_source_root() -> Path:
    spec = importlib.util.find_spec("app.providers")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.providers nicht auffindbar — zuerst linux-desktop-chat-providers "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-providers"
        )
    return Path(spec.submodule_search_locations[0])
