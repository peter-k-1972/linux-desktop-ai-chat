"""Dependency-Gruppen → Packaging-Zielmodell und Drift-Validierung."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.features.dependency_groups.models import DependencyGroupDescriptor
from app.features.dependency_groups.registry import DependencyGroupRegistry, build_default_dependency_group_registry
from app.features.dependency_packaging import (
    CANONICAL_GROUP_POLICIES,
    PackagingExtraKind,
    PackagingGroupPolicy,
    default_install_distribution_names,
    optional_dependencies_target_dict,
    packaging_target_for,
    pyproject_optional_dependencies_snippet,
    validate_availability_probe_names_align,
    validate_packaging_alignment,
    validate_pep621_pyproject_alignment,
)


def test_default_registry_packaging_alignment_clean():
    reg = build_default_dependency_group_registry()
    assert validate_packaging_alignment(reg) == []
    assert validate_availability_probe_names_align(reg) == []


def test_mapping_optional_extras_exclude_core_and_workflows():
    reg = build_default_dependency_group_registry()
    d = optional_dependencies_target_dict(reg)
    assert "core" not in d
    assert "workflows" not in d
    assert d["rag"] == ["chromadb"]
    assert d["dev"] == ["pytest", "pytest-asyncio", "pytest-qt"]
    assert d["agents"] == []


def test_core_default_install_names_match_descriptor():
    reg = build_default_dependency_group_registry()
    core = reg.get_group("core")
    assert core is not None
    assert default_install_distribution_names(reg) == core.python_packages


def test_packaging_targets_classify_known_groups():
    reg = build_default_dependency_group_registry()
    t_core = packaging_target_for(reg, "core")
    assert t_core is not None
    assert t_core.policy.extra_kind is PackagingExtraKind.BASE_INSTALL
    assert t_core.policy.include_in_default_install is True
    assert t_core.extra_name is None

    t_wf = packaging_target_for(reg, "workflows")
    assert t_wf is not None
    assert t_wf.policy.extra_kind is PackagingExtraKind.LOGICAL_MARKER
    assert t_wf.extra_name is None

    t_dev = packaging_target_for(reg, "dev")
    assert t_dev is not None
    assert t_dev.policy.dev_only is True
    assert t_dev.policy.publish_for_end_users is False
    assert t_dev.extra_name == "dev"


def test_implied_by_features_surface():
    reg = build_default_dependency_group_registry()
    t = packaging_target_for(reg, "rag")
    assert t is not None
    assert "knowledge_rag" in t.implied_by_features


def test_unknown_registry_group_triggers_packaging_error():
    reg = DependencyGroupRegistry()
    reg.register_group(
        DependencyGroupDescriptor(
            name="orphan_packaging_group_xyz",
            description="Testgruppe ohne Policy.",
            python_packages=(),
            required_for_features=frozenset(),
            optional=True,
        )
    )
    errs = validate_packaging_alignment(reg)
    assert errs
    assert any("orphan_packaging_group_xyz" in e and "Packaging-Policy" in e for e in errs)


def test_extra_policy_without_registry_triggers_error():
    reg = build_default_dependency_group_registry()
    ghost = PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=False,
    )
    with patch.dict(CANONICAL_GROUP_POLICIES, {"_policy_only_ghost_xyz": ghost}, clear=False):
        errs = validate_packaging_alignment(reg)
    assert any("_policy_only_ghost_xyz" in e for e in errs)


def test_pyproject_snippet_contains_optional_dependencies_header():
    reg = build_default_dependency_group_registry()
    text = pyproject_optional_dependencies_snippet(reg)
    assert "[project.optional-dependencies]" in text
    assert "rag = [" in text or "rag = []" in text


@pytest.mark.architecture
def test_canonical_policies_keys_match_default_registry():
    reg = build_default_dependency_group_registry()
    assert frozenset(CANONICAL_GROUP_POLICIES.keys()) == frozenset(reg.list_groups())


def test_pep621_pyproject_alignment_clean():
    """
    Vollständiger PEP-621-Drift-Check bezieht sich auf die **Host-Distribution**
    (project.dependencies / optional-dependencies wie PySide6, rag, dev, …).

    Dieses Paket (`linux-desktop-chat-features`) deklariert nur sich selbst; der
    Abgleich läuft im Host-Repo (`tools/ci/release_matrix_ci.py`, Host-pytest).
    """
    pytest.skip(
        "PEP-621-Alignment gegen Host-pyproject — im Features-Wheel nicht anwendbar"
    )


def test_optional_dependency_keys_match_packaging_dict():
    reg = build_default_dependency_group_registry()
    keys = frozenset(optional_dependencies_target_dict(reg).keys())
    assert keys == frozenset({"rag", "agents", "ops", "qml", "governance", "dev"})
    assert "workflows" not in keys
    assert "core" not in keys
