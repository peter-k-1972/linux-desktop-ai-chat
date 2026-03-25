"""Bootstrap / Edition → FeatureRegistry → Screens (ohne GUI-E2E)."""

import logging
from unittest.mock import MagicMock

import pytest

from app.features.edition_resolution import (
    DEFAULT_DESKTOP_EDITION,
    build_feature_registry_for_edition,
    resolve_active_edition_name,
)
from app.features.manifest_resolution import effective_edition_features
from app.features.registry import apply_feature_screen_registrars, build_default_feature_registry
from app.features.editions.registry import build_default_edition_registry


def test_default_edition_is_full():
    assert DEFAULT_DESKTOP_EDITION == "full"


def test_resolve_active_edition_default_no_env(monkeypatch):
    monkeypatch.delenv("LDC_EDITION", raising=False)
    assert resolve_active_edition_name(None) == "full"
    assert resolve_active_edition_name("") == "full"


def test_resolve_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("LDC_EDITION", "full")
    assert resolve_active_edition_name("minimal") == "minimal"


def test_build_minimal_registry_active_subset():
    reg = build_feature_registry_for_edition("minimal")
    assert reg.edition_name == "minimal"
    active = frozenset(reg.list_active_features())
    assert active == frozenset({"command_center", "operations_hub", "settings"})
    assert not reg.is_active("qa_governance")


def test_build_default_matches_full():
    a = build_default_feature_registry()
    b = build_feature_registry_for_edition("full")
    assert a.list_active_features() == b.list_active_features()
    assert a.edition_name == b.edition_name == "full"


def test_unknown_edition_falls_back_to_full():
    reg = build_feature_registry_for_edition("does_not_exist")
    assert reg.edition_name == "full"


def test_apply_screens_respects_edition_minimal():
    screen_reg = MagicMock()
    reg = build_feature_registry_for_edition("minimal")
    n = apply_feature_screen_registrars(reg, screen_reg)
    assert n == 3
    assert screen_reg.register.call_count == 3


def test_apply_screens_unavailable_registrar_no_crash(caplog):
    from app.features.descriptors import FeatureDescriptor
    from app.features.registry import FeatureRegistry
    from app.gui.registration.feature_builtins import register_builtin_feature_registrars

    class Ghost:
        def get_descriptor(self):
            return FeatureDescriptor(name="ghost", description="x", enabled_by_default=True)

        def register_screens(self, sr):
            raise AssertionError("should not run")

        def register_navigation(self, ctx):
            return None

        def register_commands(self, ctx):
            return None

        def register_services(self, ctx):
            return None

        def is_available(self) -> bool:
            return False

    reg = FeatureRegistry(edition_name="test")
    register_builtin_feature_registrars(reg)
    reg.register_registrar(Ghost(), enabled=True)
    reg.apply_active_feature_mask(frozenset(reg.list_registrar_names()))
    screen_reg = MagicMock()
    with caplog.at_level(logging.WARNING):
        n = apply_feature_screen_registrars(reg, screen_reg)
    assert n >= 6
    assert any("ghost" in r.getMessage().lower() for r in caplog.records)


def test_edition_descriptor_consistency_full():
    er = build_default_edition_registry()
    full = er.get_edition("full")
    assert full is not None
    eff = effective_edition_features(full)
    from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES

    assert eff == ALL_BUILTIN_FEATURE_NAMES
