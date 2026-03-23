"""Tests für tools/icon_registry_guard.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "tools" / "icon_registry_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("icon_registry_guard", GUARD)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load()


def test_registry_guard_clean_project():
    v, w, orphans = _mod.collect_registry_issues(ROOT)
    assert v == [], "\n".join(v)
    assert not orphans


def test_registry_guard_detects_bad_deployment_mapping():
    import app.gui.icons.nav_mapping as nm

    saved = dict(nm.OPS_WORKSPACE_ICONS)
    try:
        nm.OPS_WORKSPACE_ICONS = dict(nm.OPS_WORKSPACE_ICONS)
        from app.gui.icons.registry import IconRegistry

        nm.OPS_WORKSPACE_ICONS["operations_deployment"] = IconRegistry.DATA_STORES
        v, _w, _o = _mod.collect_registry_issues(ROOT)
        assert any("operations_deployment" in x for x in v)
    finally:
        nm.OPS_WORKSPACE_ICONS.clear()
        nm.OPS_WORKSPACE_ICONS.update(saved)
