"""Interne Plugin-Editionen vs. offizielle Release-Matrix."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from app.features.editions.registry import build_default_edition_registry
from app.features.release_matrix import (
    INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES,
    OFFICIAL_BUILD_RELEASE_EDITION_NAMES,
    PLUGIN_VALIDATION_SMOKE_PROFILES,
    build_internal_plugin_github_actions_matrix_payload,
    build_release_matrix,
    get_plugin_validation_smoke_profile,
    is_internal_plugin_validation_edition,
    is_official_release_edition,
    iter_internal_plugin_validation_editions,
    plugin_validation_profiles_to_json_dict,
    resolve_build_target,
    validate_internal_plugin_smoke_consistency,
    validate_release_matrix_consistency,
)


def test_official_release_edition_names_unchanged():
    assert OFFICIAL_BUILD_RELEASE_EDITION_NAMES == ("minimal", "standard", "automation", "full")


def test_plugin_example_not_official_release_target():
    assert "plugin_example" not in OFFICIAL_BUILD_RELEASE_EDITION_NAMES
    assert resolve_build_target("plugin_example") is None
    assert is_official_release_edition("plugin_example") is False
    assert is_internal_plugin_validation_edition("plugin_example") is True


def test_public_matrix_excludes_plugin_example():
    m = build_release_matrix()
    assert all(t.edition_name != "plugin_example" for t in m.targets)
    assert {t.edition_name for t in m.targets} == set(OFFICIAL_BUILD_RELEASE_EDITION_NAMES)


def test_internal_lists_disjoint():
    assert not (set(OFFICIAL_BUILD_RELEASE_EDITION_NAMES) & set(INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES))


def test_plugin_validation_profile_consistent():
    prof = get_plugin_validation_smoke_profile("plugin_example")
    assert prof is not None
    assert prof.scope_id == "internal_plugin_example_demo"
    assert "test_plugin_product_activation.py" in "".join(prof.suggested_test_paths)


def test_validate_internal_plugin_smoke_clean():
    assert validate_internal_plugin_smoke_consistency() == []


def test_validate_release_matrix_includes_internal_plugin_checks():
    assert validate_release_matrix_consistency() == []


def test_iter_internal_plugin_editions_yields_descriptor():
    er = build_default_edition_registry()
    names = [e.name for e in iter_internal_plugin_validation_editions(er)]
    assert names == ["plugin_example"]


def test_plugin_profiles_json_export():
    d = plugin_validation_profiles_to_json_dict()
    assert d["internal_plugin_validation_edition_names"] == ["plugin_example"]
    assert "plugin_example" in d["profiles"]


def test_ci_script_print_internal_plugin_json():
    repo = Path(__file__).resolve().parents[3]
    r = subprocess.run(
        [sys.executable, "tools/ci/release_matrix_ci.py", "print-internal-plugin-json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["profiles"]["plugin_example"]["edition_name"] == "plugin_example"


def test_internal_plugin_github_actions_matrix_payload():
    payload = build_internal_plugin_github_actions_matrix_payload()
    assert "include" in payload
    assert len(payload["include"]) >= 1
    row = payload["include"][0]
    assert set(row.keys()) == {"edition", "smoke_paths", "pip_extras", "install_demo_plugin"}
    assert row["edition"] in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES
    assert not is_official_release_edition(row["edition"])
    assert "dev" in row["pip_extras"]
    assert row["install_demo_plugin"] in ("true", "false")


def test_ci_script_print_internal_plugin_matrix_json():
    repo = Path(__file__).resolve().parents[3]
    r = subprocess.run(
        [sys.executable, "tools/ci/release_matrix_ci.py", "print-internal-plugin-matrix-json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert "include" in data
    assert data["include"][0]["edition"] == "plugin_example"


def test_profile_keys_match_internal_edition_names():
    assert set(PLUGIN_VALIDATION_SMOKE_PROFILES.keys()) == set(INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES)
