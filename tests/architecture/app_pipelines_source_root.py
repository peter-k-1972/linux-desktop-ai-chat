"""
Pfad zum Quellbaum von ``app.pipelines`` (Host-Workspace oder installiertes Wheel).

Nach Commit 2 liegt ``pipelines`` nicht mehr unter ``APP_ROOT/pipelines``;
Guards nutzen ``importlib.util.find_spec("app.pipelines")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-pipelines/src/app/pipelines/``.
**Nur Wheel:** ``…/site-packages/app/pipelines`` — Segment-Guards laufen weiter, solange
das Paket installiert ist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_pipelines_source_root() -> Path:
    spec = importlib.util.find_spec("app.pipelines")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.pipelines nicht auffindbar — zuerst linux-desktop-chat-pipelines "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-pipelines"
        )
    return Path(spec.submodule_search_locations[0])
