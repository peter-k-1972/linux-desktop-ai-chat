"""Produktfreigabe für externe Features: Edition ∩ Freigabe, Builtins unverändert."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.features.compatibility import FeatureSourceKind
from app.features.descriptors import FeatureDescriptor
from app.features.editions.models import EditionDescriptor
from app.features.feature_discovery import DiscoveredFeatureRegistrar, register_discovered_feature_registrars
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.manifest_resolution import (
    effective_activation_features,
    effective_edition_features,
    validate_edition_feature_references,
)
from app.features.nav_binding import collect_active_navigation_entry_ids
from app.features.registry import FeatureRegistry
from app.features.edition_resolution import build_feature_registry_for_edition
from app.gui.registration.feature_builtins import iter_builtin_feature_registrars


def test_full_edition_activation_equals_declared_features():
    from app.features.editions.registry import build_default_edition_registry

    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    assert effective_activation_features(full) == effective_edition_features(full)
    assert effective_activation_features(full) == ALL_BUILTIN_FEATURE_NAMES


def test_external_in_edition_without_release_not_activated():
    ed = EditionDescriptor(
        name="t_ext",
        description="",
        enabled_features=frozenset({"command_center", "acme.unreleased"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    assert effective_edition_features(ed) == frozenset({"command_center", "acme.unreleased"})
    assert effective_activation_features(ed) == frozenset({"command_center"})


def test_external_in_edition_with_release_activated():
    ed = EditionDescriptor(
        name="t_rel",
        description="",
        enabled_features=frozenset({"settings", "acme.released"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset({"acme.released"}),
    )
    assert effective_activation_features(ed) == frozenset({"settings", "acme.released"})


def test_validate_edition_allows_releasable_unknown_feature():
    ed = EditionDescriptor(
        name="t_val",
        description="",
        enabled_features=frozenset({"ldc.plugin.example"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset({"ldc.plugin.example"}),
    )
    known = frozenset({"command_center"})
    ok, bad = validate_edition_feature_references(ed, known)
    assert ok and bad == ()


def test_validate_edition_rejects_unknown_unreleased():
    ed = EditionDescriptor(
        name="t_bad",
        description="",
        enabled_features=frozenset({"totally.unknown.plugin"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    ok, bad = validate_edition_feature_references(ed, frozenset())
    assert not ok and bad == ("totally.unknown.plugin",)


def test_discovered_external_without_release_stays_inactive_on_full_edition():
    class _Ext:
        def get_descriptor(self) -> FeatureDescriptor:
            return FeatureDescriptor(
                name="acme.full_edition_intruder",
                description="declared in edition but not released",
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
            return True

    def fake_discover():
        for r in iter_builtin_feature_registrars():
            yield DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN)
        yield DiscoveredFeatureRegistrar(_Ext(), FeatureSourceKind.ENTRY_POINT)

    from app.features.editions.registry import build_default_edition_registry

    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    tampered = EditionDescriptor(
        name=full.name,
        description=full.description,
        enabled_features=full.enabled_features | frozenset({"acme.full_edition_intruder"}),
        disabled_features=full.disabled_features,
        released_plugin_features=full.released_plugin_features,
        dependency_groups=full.dependency_groups,
        default_shell=full.default_shell,
        experimental_allowed=full.experimental_allowed,
        visibility_profile=full.visibility_profile,
        notes=full.notes,
        support_level=full.support_level,
    )

    reg = FeatureRegistry(edition_name="full")
    with patch("app.features.feature_discovery.discover_feature_registrars", fake_discover):
        register_discovered_feature_registrars(reg)
    reg.apply_active_feature_mask(effective_activation_features(tampered))

    assert "acme.full_edition_intruder" in reg.list_registrar_names()
    assert not reg.is_registrar_enabled("acme.full_edition_intruder")
    assert not reg.is_active("acme.full_edition_intruder")


def test_plugin_example_edition_activates_example_plugin_when_discovered(monkeypatch: pytest.MonkeyPatch):
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(repo_root / "examples" / "plugins" / "ldc_plugin_example" / "src"))
    from ldc_plugin_example.feature_entry import ExamplePluginRegistrar

    def fake_discover():
        for r in iter_builtin_feature_registrars():
            yield DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN)
        yield DiscoveredFeatureRegistrar(ExamplePluginRegistrar(), FeatureSourceKind.ENTRY_POINT)

    with patch("app.features.feature_discovery.discover_feature_registrars", fake_discover):
        reg = build_feature_registry_for_edition("plugin_example")

    assert "ldc.plugin.example" in reg.list_registrar_names()
    assert reg.is_registrar_enabled("ldc.plugin.example")
    assert reg.is_active("ldc.plugin.example")


def test_navigation_skips_inactive_external_registrar():
    reg = FeatureRegistry(edition_name="t")

    class _NavExt:
        def get_descriptor(self) -> FeatureDescriptor:
            return FeatureDescriptor(
                name="acme.nav_test",
                description="x",
                navigation_entries=("nav_only_from_ext",),
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
            return True

    reg.register_registrar(_NavExt(), enabled=False)
    assert collect_active_navigation_entry_ids(reg) == frozenset()


def test_minimal_edition_unchanged():
    reg = build_feature_registry_for_edition("minimal")
    assert frozenset(reg.list_active_features()) == frozenset(
        {"command_center", "operations_hub", "settings"}
    )
