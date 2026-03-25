"""Breadcrumbs, Runtime-Subnav und Nav-Kontext — konsistent mit erlaubter Nav-Menge."""

from __future__ import annotations

import pytest

from app.features.edition_resolution import build_feature_registry_for_edition
from app.features.feature_registry import get_feature_registry, set_feature_registry
from app.features.nav_binding import collect_active_gui_command_ids
from app.gui.breadcrumbs.manager import BreadcrumbManager
from app.gui.breadcrumbs.model import BreadcrumbAction
from app.gui.domains.runtime_debug.runtime_debug_nav import RuntimeDebugNav
from app.gui.navigation.nav_areas import NavArea


@pytest.fixture(autouse=True)
def _restore_feature_registry():
    prev = get_feature_registry()
    yield
    set_feature_registry(prev)


def test_breadcrumb_blocked_workspace_falls_back_to_area():
    set_feature_registry(build_feature_registry_for_edition("minimal"))
    m = BreadcrumbManager()
    m.set_workspace(NavArea.OPERATIONS, "operations_knowledge")
    path = m.get_path()
    assert len(path) == 1
    assert path[0].action == BreadcrumbAction.AREA
    assert path[0].id == NavArea.OPERATIONS


def test_breadcrumb_hidden_area_yields_neutral_fallback():
    set_feature_registry(build_feature_registry_for_edition("minimal"))
    m = BreadcrumbManager()
    m.set_area(NavArea.CONTROL_CENTER)
    path = m.get_path()
    assert len(path) == 1
    assert path[0].id == "_nav_fallback"
    assert path[0].action == BreadcrumbAction.DETAIL


def test_breadcrumb_full_edition_shows_knowledge_workspace():
    set_feature_registry(build_feature_registry_for_edition("full"))
    m = BreadcrumbManager()
    m.set_workspace(NavArea.OPERATIONS, "operations_knowledge")
    path = m.get_path()
    assert any(it.id == "operations_knowledge" for it in path)


def test_runtime_subnav_empty_when_runtime_feature_off(monkeypatch):
    set_feature_registry(build_feature_registry_for_edition("minimal"))
    monkeypatch.setattr(
        "app.gui.devtools.devtools_visibility.is_theme_visualizer_available",
        lambda: False,
    )
    pairs = RuntimeDebugNav._build_workspace_list()
    assert pairs == []


def test_runtime_subnav_respects_allowed_ids_full(monkeypatch):
    set_feature_registry(build_feature_registry_for_edition("full"))
    monkeypatch.setattr(
        "app.gui.devtools.devtools_visibility.is_theme_visualizer_available",
        lambda: False,
    )
    pairs = RuntimeDebugNav._build_workspace_list()
    ids = {p[0] for p in pairs}
    assert "rd_logs" in ids
    assert "rd_markdown_demo" in ids


def test_minimal_edition_excludes_runtime_nav_command():
    reg = build_feature_registry_for_edition("minimal")
    cmds = collect_active_gui_command_ids(reg)
    assert "nav.rd_theme_visualizer" not in cmds
    assert "nav.runtime_debug" not in cmds
