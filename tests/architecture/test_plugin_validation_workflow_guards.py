"""
Guard: interner Plugin-Validation-Workflow bleibt von der offiziellen Release-Matrix getrennt.

Siehe docs/architecture/PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md
"""

from __future__ import annotations

import pytest

from app.features.release_matrix import PLUGIN_VALIDATION_SMOKE_PROFILES

from tests.architecture.arch_guard_config import PROJECT_ROOT

_WORKFLOW = PROJECT_ROOT / ".github/workflows" / "plugin-validation-smoke.yml"


@pytest.mark.architecture
def test_plugin_validation_workflow_invokes_internal_matrix_exporter():
    text = _WORKFLOW.read_text(encoding="utf-8")
    assert "print-internal-plugin-matrix-json" in text
    assert "print-matrix-json" not in text


@pytest.mark.architecture
def test_plugin_validation_workflow_has_no_official_edition_literals():
    text = _WORKFLOW.read_text(encoding="utf-8")
    for name in ("minimal", "standard", "automation", "full"):
        assert f"LDC_EDITION: {name}" not in text
        assert f'edition: "{name}"' not in text
        assert f"edition: {name}" not in text


@pytest.mark.architecture
def test_plugin_validation_profiles_registry_non_empty():
    assert PLUGIN_VALIDATION_SMOKE_PROFILES


@pytest.mark.architecture
def test_plugin_validation_workflow_uses_dynamic_matrix_only():
    text = _WORKFLOW.read_text(encoding="utf-8")
    assert "fromJson(needs.prepare.outputs.matrix)" in text
    assert "${{ matrix.edition }}" in text
    assert "edition-smoke-matrix.yml" not in text
