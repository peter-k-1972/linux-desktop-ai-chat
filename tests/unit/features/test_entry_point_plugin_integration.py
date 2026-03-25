"""Produktiver Entry-Point-Pfad: externe Pakete, Governance, Edition-Maske."""

from __future__ import annotations

import logging
import types
from unittest.mock import MagicMock, patch

import pytest

from app.features.compatibility import FeatureSourceKind
from app.features.descriptors import FeatureDescriptor
from app.features.feature_discovery import (
    DiscoveredFeatureRegistrar,
    register_discovered_feature_registrars,
)
from app.features.registry import FeatureRegistry
from app.features.editions.registry import build_default_edition_registry
from app.features.manifest_resolution import effective_edition_features
from app.gui.registration.feature_builtins import iter_builtin_feature_registrars

from tests.architecture.arch_guard_config import PROJECT_ROOT


def test_iter_entry_point_module_target_uses_extract_from_module():
    reg_obj = MagicMock()
    reg_obj.get_descriptor.return_value = FeatureDescriptor(
        name="acme.from_module_ep",
        description="module-style ep",
    )
    reg_obj.is_available.return_value = True

    mod = types.ModuleType("fake_ldc_ep_module")

    def _gf():
        return [reg_obj]

    mod.get_feature_registrars = _gf

    ep = MagicMock()
    ep.name = "mod_ep"
    ep.value = "fake:module"
    ep.load.return_value = mod

    mock_eps = MagicMock()
    mock_eps.select.return_value = [ep]

    with patch("importlib.metadata.entry_points", return_value=mock_eps):
        from app.features.feature_discovery import _iter_entry_point_registrars

        found = list(_iter_entry_point_registrars())
    assert len(found) == 1
    assert found[0] is reg_obj


def test_iter_entry_point_non_registrar_items_fail_soft(caplog):
    ep = MagicMock()
    ep.name = "bad_items"
    ep.value = "pkg:fn"
    ep.load.return_value = lambda: ["nope"]

    mock_eps = MagicMock()
    mock_eps.select.return_value = [ep]

    with (
        caplog.at_level(logging.WARNING, logger="app.features.feature_discovery"),
        patch("importlib.metadata.entry_points", return_value=mock_eps),
    ):
        from app.features.feature_discovery import _iter_entry_point_registrars

        assert list(_iter_entry_point_registrars()) == []
    assert any("kein FeatureRegistrar" in r.getMessage() for r in caplog.records)


def test_entry_point_governance_rejects_invalid_feature_name():
    bad = MagicMock()
    bad.get_descriptor.return_value = FeatureDescriptor(
        name="invalidname_without_namespace",
        description="bad",
    )
    bad.is_available.return_value = True

    def fake_discover():
        for r in iter_builtin_feature_registrars():
            yield DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN)
        yield DiscoveredFeatureRegistrar(bad, FeatureSourceKind.ENTRY_POINT)

    reg = FeatureRegistry(edition_name="t")
    with patch("app.features.feature_discovery.discover_feature_registrars", fake_discover):
        n = register_discovered_feature_registrars(reg)
    assert n == len(tuple(iter_builtin_feature_registrars()))
    assert "invalidname_without_namespace" not in reg.list_registrar_names()


def test_external_style_registrar_registers_and_edition_disables():
    class _OkExt:
        def get_descriptor(self) -> FeatureDescriptor:
            return FeatureDescriptor(
                name="ldc.plugin.example",
                description="external-style name",
            )

        def register_screens(self, screen_registry):
            return None

        def register_navigation(self, context):
            return None

        def register_commands(self, context):
            return None

        def register_services(self, context):
            return None

        def is_available(self) -> bool:
            return True

    def fake_discover():
        for r in iter_builtin_feature_registrars():
            yield DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN)
        yield DiscoveredFeatureRegistrar(_OkExt(), FeatureSourceKind.ENTRY_POINT)

    reg = FeatureRegistry(edition_name="minimal")
    with patch("app.features.feature_discovery.discover_feature_registrars", fake_discover):
        register_discovered_feature_registrars(reg)

    assert "ldc.plugin.example" in reg.list_registrar_names()
    er = build_default_edition_registry()
    minimal = er.get_edition("minimal")
    assert minimal is not None
    eff = effective_edition_features(minimal)
    reg.apply_active_feature_mask(eff)
    assert reg.is_registrar_enabled("ldc.plugin.example") is False


def test_example_plugin_package_layout():
    root = PROJECT_ROOT / "examples" / "plugins" / "ldc_plugin_example"
    assert (root / "pyproject.toml").is_file()
    assert (root / "src" / "ldc_plugin_example" / "feature_entry.py").is_file()
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "linux_desktop_chat.features" in text
    assert "get_feature_registrars" in text


def test_example_plugin_src_importable(monkeypatch: pytest.MonkeyPatch):
    src = PROJECT_ROOT / "examples" / "plugins" / "ldc_plugin_example" / "src"
    monkeypatch.syspath_prepend(str(src))
    from ldc_plugin_example.feature_entry import get_feature_registrars

    regs = get_feature_registrars()
    assert len(regs) == 1
    assert regs[0].get_descriptor().name == "ldc.plugin.example"
