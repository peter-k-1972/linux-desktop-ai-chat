"""FeatureRegistry, Deskriptoren — ohne globale Default-Registry."""

from unittest.mock import MagicMock

import pytest

from app.features.descriptors import FeatureDescriptor
from app.features.feature_manifest import iter_default_feature_descriptors
from app.features.registry import (
    FeatureRegistry,
    apply_feature_screen_registrars,
    build_default_feature_registry,
    get_feature_registry,
    set_feature_registry,
)


def test_register_registrar_and_get_descriptor():
    from app.gui.registration.feature_builtins import CommandCenterFeatureRegistrar

    reg = FeatureRegistry()
    r = CommandCenterFeatureRegistrar()
    reg.register_registrar(r)
    assert reg.get_registrar("command_center") is r
    assert reg.get_feature("command_center") == r.get_descriptor()


def test_list_enabled_registrars_builtin_count():
    reg = build_default_feature_registry()
    names = [x.get_descriptor().name for x in reg.list_enabled_registrars()]
    assert "operations_hub" in names
    assert "qa_governance" in names
    assert "knowledge_rag" in names
    assert len(names) >= 8


def test_duplicate_registrar_raises():
    from app.gui.registration.feature_builtins import CommandCenterFeatureRegistrar

    reg = FeatureRegistry()
    reg.register_registrar(CommandCenterFeatureRegistrar())
    with pytest.raises(ValueError, match="bereits registriert"):
        reg.register_registrar(CommandCenterFeatureRegistrar())


def test_default_manifest_descriptors_match_registry():
    reg = build_default_feature_registry()
    from_reg = tuple(r.get_descriptor().name for r in reg.list_registrars())
    from_iter = tuple(d.name for d in iter_default_feature_descriptors())
    assert from_reg == from_iter


def test_apply_screens_invokes_all_screen_registrars():
    screen_reg = MagicMock()
    reg = build_default_feature_registry()
    n = apply_feature_screen_registrars(reg, screen_reg)
    assert n == len(reg.list_enabled_registrars())
    # Sechs Top-Level-Nav-Screens; Capability-Registrare rufen register_screens ohne register():
    assert screen_reg.register.call_count == 6


def test_unavailable_registrar_skipped_in_enabled_list():
    class Unavail:
        def get_descriptor(self):
            return FeatureDescriptor(
                name="ghost",
                description="x",
                enabled_by_default=True,
                screens=("command_center",),
            )

        def register_screens(self, sr):
            sr.register("should_not_run", lambda: None, "")

        def register_navigation(self, ctx):
            return None

        def register_commands(self, ctx):
            return None

        def register_services(self, ctx):
            return None

        def is_available(self) -> bool:
            return False

    from app.gui.registration.feature_builtins import CommandCenterFeatureRegistrar

    reg = FeatureRegistry()
    reg.register_registrar(Unavail())
    reg.register_registrar(CommandCenterFeatureRegistrar())
    enabled = reg.list_enabled_registrars()
    assert len(enabled) == 1
    assert enabled[0].get_descriptor().name == "command_center"


def test_set_get_feature_registry_roundtrip():
    prev = get_feature_registry()
    try:
        reg = build_default_feature_registry()
        set_feature_registry(reg)
        assert get_feature_registry() is reg
    finally:
        set_feature_registry(prev)


def test_register_feature_legacy_wrapper():
    reg = FeatureRegistry()
    d = FeatureDescriptor(name="legacy_x", description="legacy")
    reg.register_feature(d, active=True)
    assert reg.get_feature("legacy_x") is d
    assert "legacy_x" in reg.list_active_features()

