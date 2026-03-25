"""Build-/Release-Matrix aus Editionen."""

from __future__ import annotations

from pathlib import Path

from app.features.edition_resolution import DEFAULT_DESKTOP_EDITION
from app.features.editions.registry import build_default_edition_registry
from app.features.manifest_resolution import edition_declared_and_implied_dependency_groups
from app.features.dependency_groups.registry import build_default_dependency_group_registry
from app.features.release_matrix import (
    OFFICIAL_BUILD_RELEASE_EDITION_NAMES,
    REFERENCE_BUILD_EDITION_NAME,
    ReleaseMatrix,
    artifact_name_for_edition,
    build_release_matrix,
    edition_build_target_to_json_dict,
    pip_overlay_distribution_names_for_target,
    release_matrix_to_json_dict,
    resolve_build_target,
    validate_release_matrix_consistency,
)

_HOST_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_official_editions_have_build_targets():
    m = build_release_matrix()
    names = {t.edition_name for t in m.targets}
    assert names == set(OFFICIAL_BUILD_RELEASE_EDITION_NAMES)
    assert len(m.targets) == len(OFFICIAL_BUILD_RELEASE_EDITION_NAMES)


def test_build_targets_reference_known_editions():
    er = build_default_edition_registry()
    m = build_release_matrix(edition_registry=er)
    for t in m.targets:
        assert er.get_edition(t.edition_name) is not None


def test_derived_dependency_groups_match_manifest_resolution():
    er = build_default_edition_registry()
    dr = build_default_dependency_group_registry()
    m = build_release_matrix(edition_registry=er, dep_registry=dr)
    for t in m.targets:
        ed = er.get_edition(t.edition_name)
        assert ed is not None
        expected = edition_declared_and_implied_dependency_groups(ed, dr)
        assert frozenset(t.dependency_groups) == expected


def test_artifact_names_unique_and_stable():
    m = build_release_matrix()
    names = [t.artifact_name for t in m.targets]
    assert len(names) == len(set(names))
    assert artifact_name_for_edition("minimal") == "linux-desktop-chat-minimal"
    assert artifact_name_for_edition("full") == "linux-desktop-chat-full"


def test_smoke_scopes_and_paths_present():
    m = build_release_matrix()
    for t in m.targets:
        assert t.smoke_test_scope
        assert t.pytest_markers
        assert t.suggested_smoke_paths


def test_reference_edition_matches_default_desktop():
    assert REFERENCE_BUILD_EDITION_NAME == DEFAULT_DESKTOP_EDITION
    m = build_release_matrix()
    refs = [t for t in m.targets if t.is_reference_edition]
    assert len(refs) == 1
    assert refs[0].edition_name == REFERENCE_BUILD_EDITION_NAME == "full"


def test_pip_runtime_extras_subset_of_groups_no_dev():
    m = build_release_matrix()
    for t in m.targets:
        assert "dev" not in t.pip_runtime_extras
        assert set(t.pip_runtime_extras) <= set(t.dependency_groups)


def test_workflows_group_has_no_pip_extra_in_targets():
    """LOGICAL_MARKER ``workflows`` — in Gruppenmenge, aber nicht in pip_runtime_extras."""
    m = build_release_matrix()
    auto = next(t for t in m.targets if t.edition_name == "automation")
    assert "workflows" in auto.dependency_groups
    assert "workflows" not in auto.pip_runtime_extras


def test_validate_release_matrix_clean():
    assert validate_release_matrix_consistency(repo_root=_HOST_REPO_ROOT) == []


def test_resolve_build_target_unknown_returns_none():
    assert resolve_build_target("nonexistent_edition_xyz") is None


def test_json_export_roundtrip_keys():
    m = build_release_matrix()
    d = release_matrix_to_json_dict(m)
    assert d["reference_edition_name"] == REFERENCE_BUILD_EDITION_NAME
    assert len(d["targets"]) == len(m.targets)
    first = edition_build_target_to_json_dict(m.targets[0])
    assert "pip_runtime_extras" in first and "dependency_groups" in first


def test_validation_fails_on_fake_matrix_wrong_groups():
    from dataclasses import replace

    er = build_default_edition_registry()
    dr = build_default_dependency_group_registry()
    m = build_release_matrix(edition_registry=er, dep_registry=dr)
    fixed_targets = tuple(
        replace(t, dependency_groups=("no_such_group_xyz",))
        if t.edition_name == "minimal"
        else t
        for t in m.targets
    )
    bad_matrix = ReleaseMatrix(
        targets=fixed_targets,
        official_edition_names=OFFICIAL_BUILD_RELEASE_EDITION_NAMES,
        reference_edition_name=REFERENCE_BUILD_EDITION_NAME,
    )
    errs = validate_release_matrix_consistency(
        bad_matrix, edition_registry=er, dep_registry=dr, repo_root=_HOST_REPO_ROOT
    )
    assert any("no_such_group_xyz" in e for e in errs)


def test_pip_overlay_includes_dev_and_runtime_extras_packages():
    dr = build_default_dependency_group_registry()
    m = build_release_matrix(dep_registry=dr)
    std = next(t for t in m.targets if t.edition_name == "standard")
    overlay = pip_overlay_distribution_names_for_target(std, dr)
    assert "chromadb" in overlay
    assert "pytest" in overlay


def test_ci_script_print_matrix_json_exit_zero():
    import json
    import subprocess
    import sys
    from pathlib import Path

    r = subprocess.run(
        [sys.executable, "tools/ci/release_matrix_ci.py", "print-matrix-json"],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    row0 = data["include"][0]
    assert "pip_extras" in row0
    assert "edition" in row0
    assert "agents" in row0["pip_extras"] or "dev" in row0["pip_extras"]
