"""
Pfad zum Quellbaum von ``app.ui_contracts`` (Host-Workspace oder installiertes Wheel).

Nach Commit 2 liegt ``ui_contracts`` nicht mehr unter ``APP_ROOT/ui_contracts``;
Guards nutzen ``importlib.util.find_spec("app.ui_contracts")`` bzw. diese Hilfsfunktion.

**Monorepo:** typisch editable ``linux-desktop-chat-ui-contracts/src/app/ui_contracts/``.
**Nur Wheel:** ``…/site-packages/app/ui_contracts`` — Segment-Guards laufen weiter, solange
das Paket installiert ist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def app_ui_contracts_source_root() -> Path:
    spec = importlib.util.find_spec("app.ui_contracts")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(
            "app.ui_contracts nicht auffindbar — zuerst linux-desktop-chat-ui-contracts "
            "installieren, z. B.: python3 -m pip install -e ./linux-desktop-chat-ui-contracts"
        )
    return Path(spec.submodule_search_locations[0])
