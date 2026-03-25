"""
Pfad zum Quellbaum von ``app.cli`` (Host-Workspace oder installiertes Wheel).

Nach Commit 2 liegt ``cli`` nicht mehr unter ``APP_ROOT/cli``;
Guards nutzen ``importlib.util.find_spec("app.cli")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-cli/src/app/cli/``.
**Nur Wheel:** ``…/site-packages/app/cli`` — Segment-Guards laufen weiter, solange
das Paket installiert ist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_cli_source_root() -> Path:
    spec = importlib.util.find_spec("app.cli")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.cli nicht auffindbar — zuerst linux-desktop-chat-cli "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-cli"
        )
    return Path(spec.submodule_search_locations[0])
