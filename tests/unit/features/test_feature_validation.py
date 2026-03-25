"""Governance / Validierung für discoverbare FeatureRegistrare."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from app.features.compatibility import (
    FEATURE_HOST_PLATFORM_VERSION,
    FeatureCompatibility,
    FeatureSourceKind,
    resolve_feature_compatibility,
)
from app.features.descriptors import FeatureDescriptor
from app.features.dependency_groups.registry import build_default_dependency_group_registry
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.feature_validation import (
    plan_registration_order,
    validate_feature_compatibility,
    validate_feature_descriptor,
    validate_feature_name,
    validate_feature_registrar,
)
from app.features.registry import FeatureRegistry
from app.gui.registration.feature_builtins import iter_builtin_feature_registrars


@pytest.fixture
def dep_group_names():
    reg = build_default_dependency_group_registry()
    return frozenset(reg.list_groups())


def test_validate_feature_descriptor_requires_description():
    d = FeatureDescriptor(name="plugin_x", description="")
    r = validate_feature_descriptor(d)
    assert not r.ok


def test_validate_feature_name_builtin_must_be_catalog():
    r = validate_feature_name("not_a_builtin", FeatureSourceKind.BUILTIN)
    assert not r.ok
    r2 = validate_feature_name("knowledge_rag", FeatureSourceKind.BUILTIN)
    assert r2.ok


def test_validate_feature_name_extension_reserved_and_prefix():
    r = validate_feature_name("knowledge_rag", FeatureSourceKind.PLUGIN)
    assert not r.ok
    r2 = validate_feature_name("bad-name", FeatureSourceKind.PLUGIN)
    assert not r2.ok
    assert validate_feature_name("plugin_audio_tools", FeatureSourceKind.PLUGIN).ok
    assert validate_feature_name("ext_audio_tools", FeatureSourceKind.EXTENSION).ok
    assert validate_feature_name("acme.audio_tools", FeatureSourceKind.ENTRY_POINT).ok


def test_validate_feature_compatibility_unknown_dependency_group(dep_group_names):
    desc = FeatureDescriptor(
        name="plugin_z",
        description="z",
        optional_dependencies=("no_such_group_xyz",),
    )
    c = resolve_feature_compatibility(_SimpleReg(desc), source_kind=FeatureSourceKind.PLUGIN)
    r = validate_feature_compatibility(
        c,
        descriptor_name=desc.name,
        known_dependency_group_names=dep_group_names,
    )
    assert not r.ok
    assert any("Unbekannte Dependency-Gruppe" in e for e in r.errors)


def test_validate_feature_compatibility_host_range():
    c = FeatureCompatibility(
        feature_name="plugin_host",
        api_version="1",
        min_host_version="99",
        max_host_version=None,
        requires_features=(),
        incompatible_features=(),
        declared_dependency_groups=(),
        source_kind=FeatureSourceKind.PLUGIN,
    )
    r = validate_feature_compatibility(
        c,
        descriptor_name="plugin_host",
        known_dependency_group_names=frozenset(),
        host_version=FEATURE_HOST_PLATFORM_VERSION,
    )
    assert not r.ok


def test_plan_registration_order_rejects_duplicate_extension(dep_group_names):
    d = FeatureDescriptor(name="plugin_dup_test", description="d")
    reg = MagicMock(spec=["get_descriptor"])
    reg.get_descriptor.return_value = d

    planned = plan_registration_order(
        [(reg, FeatureSourceKind.PLUGIN), (reg, FeatureSourceKind.PLUGIN)],
        known_dependency_group_names=dep_group_names,
        log=logging.getLogger("test_dup"),
    )
    assert len(planned) == 1


def test_plan_registration_order_incompatible_skips_second(dep_group_names):
    d1 = FeatureDescriptor(name="plugin_inc_first", description="a")
    r1 = MagicMock(spec=["get_descriptor"])
    r1.get_descriptor.return_value = d1

    d2 = FeatureDescriptor(name="plugin_inc_second", description="b")

    def _compat2():
        return FeatureCompatibility(
            feature_name="plugin_inc_second",
            api_version="1",
            min_host_version=None,
            max_host_version=None,
            requires_features=(),
            incompatible_features=("plugin_inc_first",),
            declared_dependency_groups=(),
            source_kind=FeatureSourceKind.PLUGIN,
        )

    r2 = MagicMock(spec=["get_descriptor", "get_feature_compatibility"])
    r2.get_descriptor.return_value = d2
    r2.get_feature_compatibility = _compat2

    planned = plan_registration_order(
        [(r1, FeatureSourceKind.PLUGIN), (r2, FeatureSourceKind.PLUGIN)],
        known_dependency_group_names=dep_group_names,
        log=logging.getLogger("test_inc"),
    )
    assert [p[0].get_descriptor().name for p in planned] == ["plugin_inc_first"]


def test_plan_registration_order_accepts_valid_extension(dep_group_names):
    d = FeatureDescriptor(
        name="plugin_ok_governance_test",
        description="ok",
        optional_dependencies=("rag",),
    )
    reg = MagicMock(spec=["get_descriptor"])
    reg.get_descriptor.return_value = d
    planned = plan_registration_order(
        [(reg, FeatureSourceKind.PLUGIN)],
        known_dependency_group_names=dep_group_names,
        log=logging.getLogger("test_ok"),
    )
    assert len(planned) == 1


def test_validate_feature_registrar_requires_feature_name_known(dep_group_names):
    d = FeatureDescriptor(name="plugin_needs_unknown", description="x")

    def _compat():
        return FeatureCompatibility(
            feature_name="plugin_needs_unknown",
            api_version="1",
            min_host_version=None,
            max_host_version=None,
            requires_features=("no_such_feature_xyz",),
            incompatible_features=(),
            declared_dependency_groups=(),
            source_kind=FeatureSourceKind.PLUGIN,
        )

    reg = MagicMock(spec=["get_descriptor", "get_feature_compatibility"])
    reg.get_descriptor.return_value = d
    reg.get_feature_compatibility = _compat

    v = validate_feature_registrar(
        reg,
        source_kind=FeatureSourceKind.PLUGIN,
        known_dependency_group_names=dep_group_names,
        accepted_feature_names=frozenset(ALL_BUILTIN_FEATURE_NAMES),
    )
    assert not v.ok


def test_builtin_registrars_pass_validation(dep_group_names):
    for reg in iter_builtin_feature_registrars():
        v = validate_feature_registrar(
            reg,
            source_kind=FeatureSourceKind.BUILTIN,
            known_dependency_group_names=dep_group_names,
            accepted_feature_names=frozenset(ALL_BUILTIN_FEATURE_NAMES),
        )
        assert v.ok, (reg.get_descriptor().name, v.errors)


def test_register_discovered_builtin_count_unchanged():
    reg = FeatureRegistry(edition_name="gov")
    from app.features.feature_discovery import register_discovered_feature_registrars

    n = register_discovered_feature_registrars(reg)
    assert n == len(tuple(iter_builtin_feature_registrars()))


class _SimpleReg:
    def __init__(self, d: FeatureDescriptor) -> None:
        self._d = d

    def get_descriptor(self) -> FeatureDescriptor:
        return self._d
