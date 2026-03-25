"""FeatureRegistrar-Discovery (Builtins, Plugins, Entry Points, Env)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from app.features.descriptors import FeatureDescriptor
from app.features.compatibility import FeatureSourceKind
from app.features.feature_discovery import (
    DiscoveredFeatureRegistrar,
    discover_feature_registrars,
    register_discovered_feature_registrars,
)
from app.features.registry import FeatureRegistry
from app.gui.registration.feature_builtins import iter_builtin_feature_registrars


def test_discover_includes_all_builtin_registrars():
    discovered = discover_feature_registrars()
    builtin = tuple(iter_builtin_feature_registrars())
    assert len(discovered) >= len(builtin)
    d_names = [r.registrar.get_descriptor().name for r in discovered[: len(builtin)]]
    b_names = [r.get_descriptor().name for r in builtin]
    assert d_names == b_names
    assert all(r.source_kind is FeatureSourceKind.BUILTIN for r in discovered[: len(builtin)])


def test_register_discovered_populates_registry():
    reg = FeatureRegistry(edition_name="x")
    n = register_discovered_feature_registrars(reg)
    assert n == len(tuple(iter_builtin_feature_registrars()))
    assert n == len(reg.list_registrar_names())


def test_duplicate_from_discovery_logs_warning(caplog):
    ghost = MagicMock()
    ghost.get_descriptor.return_value = FeatureDescriptor(
        name="command_center",
        description="collision",
    )
    ghost.is_available.return_value = True

    def fake_discover():
        for r in iter_builtin_feature_registrars():
            yield DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN)
        yield DiscoveredFeatureRegistrar(ghost, FeatureSourceKind.PLUGIN)

    reg = FeatureRegistry(edition_name="t")
    with caplog.at_level(logging.WARNING, logger="app.features.feature_discovery"), patch(
        "app.features.feature_discovery.discover_feature_registrars",
        fake_discover,
    ):
        n = register_discovered_feature_registrars(reg)
    assert n == len(tuple(iter_builtin_feature_registrars()))
    assert any("übersprungen" in r.getMessage().lower() for r in caplog.records)


def test_iter_entry_point_registrars_mocked():
    reg_obj = MagicMock()
    reg_obj.get_descriptor.return_value = FeatureDescriptor(
        name="plugin_entry_point_only_feature_xyz",
        description="from ep",
    )
    ep = MagicMock()
    ep.name = "test_ep"
    ep.value = "test:load"
    ep.load.return_value = lambda: [reg_obj]

    mock_eps = MagicMock()
    mock_eps.select.return_value = [ep]

    with patch("importlib.metadata.entry_points", return_value=mock_eps):
        from app.features.feature_discovery import _iter_entry_point_registrars

        extra = list(_iter_entry_point_registrars())
    assert len(extra) == 1
    assert extra[0] is reg_obj


def test_iter_env_module_registrars(monkeypatch):
    mod = MagicMock()

    def getregs():
        r = MagicMock()
        r.get_descriptor.return_value = FeatureDescriptor(
            name="ext_env_only_feature_xyz",
            description="env",
        )
        r.is_available.return_value = True
        return [r]

    mod.get_feature_registrars = getregs
    monkeypatch.setitem(__import__("sys").modules, "test_ldc_env_reg_mod", mod)
    monkeypatch.setenv("LDC_FEATURE_REGISTRAR_MODULES", "test_ldc_env_reg_mod")

    from app.features.feature_discovery import _iter_env_module_registrars

    extra = list(_iter_env_module_registrars())
    assert len(extra) == 1
    assert extra[0].get_descriptor().name == "ext_env_only_feature_xyz"


def test_plugin_package_discovery_patched():
    fr = MagicMock()
    fr.get_descriptor.return_value = FeatureDescriptor(
        name="plugin_stub_feature_xyz",
        description="plugin",
    )
    fr.is_available.return_value = True

    def fake_pkg(name: str):
        if name == "app.plugins":
            yield fr

    with patch("app.features.feature_discovery._iter_subpackage_feature_registrars", fake_pkg):
        out = discover_feature_registrars()
    names = [r.registrar.get_descriptor().name for r in out]
    assert "plugin_stub_feature_xyz" in names


def test_missing_plugin_submodules_no_crash():
    """Leere app.plugins / app.extensions — kein Absturz."""
    out = discover_feature_registrars()
    assert len(out) >= len(tuple(iter_builtin_feature_registrars()))
