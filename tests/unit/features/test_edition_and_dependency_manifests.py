"""Edition- und Dependency-Group-Manifeste (ohne Laufzeit-Gating)."""

import pytest

from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.manifest_resolution import (
    dependency_groups_implied_by_features,
    edition_declared_and_implied_dependency_groups,
    effective_edition_features,
    validate_dependency_group_feature_references,
    validate_edition_dependency_group_references,
    validate_edition_feature_references,
)
from app.features.registry import build_default_feature_registry
from app.features.dependency_groups.registry import (
    DependencyGroupRegistry,
    build_default_dependency_group_registry,
)
from app.features.editions.registry import EditionRegistry, build_default_edition_registry


def test_edition_registry_builtin_count():
    reg = build_default_edition_registry()
    assert reg.list_editions() == ("minimal", "standard", "automation", "full", "plugin_example")


def test_dependency_group_registry_builtin_count():
    reg = build_default_dependency_group_registry()
    assert "core" in reg.list_groups()
    assert "rag" in reg.list_groups()
    assert "governance" in reg.list_groups()
    assert "dev" in reg.list_groups()


def test_edition_features_are_known_features():
    known = frozenset(build_default_feature_registry().list_registrar_names())
    assert ALL_BUILTIN_FEATURE_NAMES <= known
    editions = build_default_edition_registry()
    for ed in editions.iter_editions():
        ok, bad = validate_edition_feature_references(ed, known)
        assert ok, f"edition {ed.name}: unknown {bad}"


def test_dependency_groups_reference_valid_features():
    known = ALL_BUILTIN_FEATURE_NAMES
    deps = build_default_dependency_group_registry()
    for g in deps.iter_groups():
        ok, bad = validate_dependency_group_feature_references(
            g.name, g.required_for_features, known
        )
        assert ok, f"group {g.name}: unknown features {bad}"


def test_edition_dependency_group_names_exist():
    deps = build_default_dependency_group_registry()
    known_g = frozenset(deps.list_groups())
    for ed in build_default_edition_registry().iter_editions():
        ok, bad = validate_edition_dependency_group_references(ed, known_g)
        assert ok, f"edition {ed.name}: unknown groups {bad}"


def test_effective_edition_features_respects_disabled():
    from app.features.editions.models import EditionDescriptor

    ed = EditionDescriptor(
        name="t",
        description="",
        enabled_features=frozenset({"a", "b"}),
        disabled_features=frozenset({"b"}),
    )
    assert effective_edition_features(ed) == frozenset({"a"})


def test_implied_groups_include_core_for_any_feature_subset():
    deps = build_default_dependency_group_registry()
    implied = dependency_groups_implied_by_features(frozenset({"settings"}), deps)
    assert "core" in implied


def test_full_edition_covers_all_catalog_features():
    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    assert effective_edition_features(full) == ALL_BUILTIN_FEATURE_NAMES


def test_duplicate_edition_registration_raises():
    reg = EditionRegistry()
    e = build_default_edition_registry().get_edition("minimal")
    assert e is not None
    reg.register_edition(e)
    with pytest.raises(ValueError, match="bereits registriert"):
        reg.register_edition(e)


def test_union_declared_and_implied_groups():
    ed = build_default_edition_registry().get_edition("minimal")
    deps = build_default_dependency_group_registry()
    assert ed is not None
    u = edition_declared_and_implied_dependency_groups(ed, deps)
    assert "core" in u
    assert u >= frozenset(ed.dependency_groups)
