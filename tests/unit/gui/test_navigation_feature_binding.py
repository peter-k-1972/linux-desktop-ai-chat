"""Edition-/Feature-gefilterte Navigation (Sidebar, Nav-Binding, ohne GUI-E2E)."""

from __future__ import annotations

import logging

import pytest

from app.features.edition_resolution import build_feature_registry_for_edition
from app.features.feature_registry import get_feature_registry, set_feature_registry
from app.features.nav_binding import (
    collect_active_gui_command_ids,
    collect_active_navigation_entry_ids,
)
from app.features.registry import FeatureRegistry
from app.gui.navigation.sidebar_config import get_sidebar_sections
from app.gui.registration.feature_builtins import register_builtin_feature_registrars


@pytest.fixture(autouse=True)
def _restore_feature_registry():
    prev = get_feature_registry()
    yield
    set_feature_registry(prev)


def _all_nav_keys(sections):
    return {it.nav_key for sec in sections for it in sec.items}


def test_minimal_edition_navigation_ids_exclude_capability_workspaces():
    reg = build_feature_registry_for_edition("minimal")
    ids = collect_active_navigation_entry_ids(reg)
    assert "operations_knowledge" not in ids
    assert "operations_prompt_studio" not in ids
    assert "operations_workflows" not in ids
    assert "cc_models" not in ids
    assert "operations_chat" in ids
    assert "command_center" in ids


def test_full_edition_includes_capability_and_control_nav_ids():
    reg = build_feature_registry_for_edition("full")
    ids = collect_active_navigation_entry_ids(reg)
    assert "operations_knowledge" in ids
    assert "cc_models" in ids
    assert "qa_test_inventory" in ids


def test_minimal_sidebar_matches_active_nav_ids():
    reg = build_feature_registry_for_edition("minimal")
    sections = get_sidebar_sections(feature_registry=reg)
    keys = _all_nav_keys(sections)
    allowed = collect_active_navigation_entry_ids(reg)
    assert keys <= allowed
    assert "operations_knowledge" not in keys


def test_full_sidebar_covers_all_active_nav_entries():
    reg = build_feature_registry_for_edition("full")
    sections = get_sidebar_sections(feature_registry=reg)
    keys = _all_nav_keys(sections)
    allowed = collect_active_navigation_entry_ids(reg)
    assert keys == allowed


def test_minimal_gui_commands_exclude_knowledge_nav():
    reg = build_feature_registry_for_edition("minimal")
    cmds = collect_active_gui_command_ids(reg)
    assert "nav.knowledge" not in cmds
    assert "nav.chat" in cmds
    assert "nav.cc_models" not in cmds


def test_unavailable_registrar_drops_navigation_entries(caplog):
    from app.features.descriptors import FeatureDescriptor

    class Ghost:
        def get_descriptor(self):
            return FeatureDescriptor(
                name="ghost",
                description="x",
                navigation_entries=("command_center",),
                commands=("nav.dashboard",),
            )

        def register_screens(self, sr):
            return None

        def register_navigation(self, ctx):
            return None

        def register_commands(self, ctx):
            return None

        def register_services(self, ctx):
            return None

        def is_available(self) -> bool:
            return False

    reg = FeatureRegistry(edition_name="t")
    register_builtin_feature_registrars(reg)
    reg.register_registrar(Ghost(), enabled=True)
    reg.apply_active_feature_mask(frozenset(reg.list_registrar_names()))
    with caplog.at_level(logging.WARNING):
        ids = collect_active_navigation_entry_ids(reg)
    assert "command_center" in ids  # from command_center feature, not ghost
    assert any("ghost" in r.getMessage().lower() for r in caplog.records)
