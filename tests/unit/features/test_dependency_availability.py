"""Zentrale Dependency-/Feature-Availability (ohne globales LDC_IGNORE für diese Datei)."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from app.features.availability_types import AvailabilityResult
from app.features.dependency_availability import (
    check_dependency_group_availability,
    check_feature_availability,
    is_module_importable,
    is_feature_technically_available,
    register_group_probe,
)
from app.features.dependency_groups.registry import build_default_dependency_group_registry
from app.features.descriptors import FeatureDescriptor
from app.features.registry import FeatureRegistry, apply_feature_screen_registrars
from app.gui.registration.feature_builtins import (
    KnowledgeRAGCapabilityRegistrar,
    register_builtin_feature_registrars,
)


@pytest.fixture(autouse=True)
def _enable_real_technical_availability(monkeypatch):
    monkeypatch.setenv("LDC_IGNORE_TECHNICAL_AVAILABILITY", "0")


@pytest.fixture(autouse=True)
def _restore_dependency_group_probes_after_test():
    import app.features.dependency_availability as dav

    snap = dict(dav._GROUP_PROBES)
    yield
    dav._GROUP_PROBES.clear()
    dav._GROUP_PROBES.update(snap)


def test_availability_result_fields():
    r = AvailabilityResult(False, "x", "msg", missing_modules=("m",))
    assert r.available is False
    assert r.reason_code == "x"
    assert r.missing_modules == ("m",)


def test_is_module_importable_stdlib():
    r = is_module_importable("json")
    assert r.available is True
    assert r.reason_code == "ok"


def test_is_module_importable_missing():
    r = is_module_importable("definitely_not_a_module_xyz_12345")
    assert r.available is False
    assert r.reason_code == "import_failed"


def test_check_unknown_dependency_group():
    r = check_dependency_group_availability(
        "no_such_group_ever",
        dep_registry=build_default_dependency_group_registry(),
    )
    assert r.available is False
    assert r.reason_code == "unknown_group"


def test_rag_group_respects_stub_probe():
    reg = build_default_dependency_group_registry()
    register_group_probe("rag", lambda: AvailabilityResult(True, "ok", "stub"))
    r = check_dependency_group_availability("rag", dep_registry=reg)
    assert r.available is True


def test_feature_knowledge_requires_rag():
    reg = build_default_dependency_group_registry()
    register_group_probe("rag", lambda: AvailabilityResult(False, "import_failed", "no chroma"))
    d = KnowledgeRAGCapabilityRegistrar().get_descriptor()
    fa = check_feature_availability(d, dep_registry=reg, require_core=False)
    assert fa.available is False
    assert fa.failed_group == "rag"
    assert fa.group_result is not None
    assert not fa.group_result.available


def test_feature_without_extra_deps_ok():
    d = FeatureDescriptor(
        name="x",
        description="y",
        optional_dependencies=(),
    )
    fa = check_feature_availability(d, require_core=False)
    assert fa.available is True


def test_unavailable_feature_skips_screen_registration():
    reg = FeatureRegistry(edition_name="t")
    register_builtin_feature_registrars(reg)
    reg.apply_active_feature_mask(frozenset({"knowledge_rag"}))

    register_group_probe("rag", lambda: AvailabilityResult(False, "import_failed", "missing"))

    assert not is_feature_technically_available(reg.get_registrar("knowledge_rag").get_descriptor())

    screen_reg = MagicMock()
    n = apply_feature_screen_registrars(reg, screen_reg)
    assert n == 0


def test_registry_path_no_crash_when_group_probe_fails():
    reg = FeatureRegistry(edition_name="t")
    register_builtin_feature_registrars(reg)
    reg.apply_active_feature_mask(frozenset({"knowledge_rag"}))
    register_group_probe("rag", lambda: AvailabilityResult(False, "import_failed", "x"))
    assert reg.list_active_features() == ()


def test_builtin_optional_dependency_names_are_registered_groups():
    from app.gui.registration import feature_builtins as fb

    dep = build_default_dependency_group_registry()
    known = frozenset(dep.list_groups())
    for name in (
        "CommandCenterFeatureRegistrar",
        "OperationsHubFeatureRegistrar",
        "ControlCenterFeatureRegistrar",
        "QAGovernanceFeatureRegistrar",
        "RuntimeObservabilityFeatureRegistrar",
        "SettingsFeatureRegistrar",
        "PromptStudioCapabilityRegistrar",
        "KnowledgeRAGCapabilityRegistrar",
        "WorkflowAutomationCapabilityRegistrar",
    ):
        cls = getattr(fb, name)
        for tag in cls().get_descriptor().optional_dependencies:
            assert tag in known, f"{name}: unknown group {tag!r}"
