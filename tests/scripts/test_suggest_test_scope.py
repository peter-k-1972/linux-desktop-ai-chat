from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "suggest_test_scope.py"


def run_script(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        input=input_text,
    )


def test_global_overlay_mapping():
    result = run_script("app/global_overlay/overlay_manager.py")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "tests/architecture/test_gui_domain_dependency_guards.py",
        "tests/architecture/test_gui_governance_guards.py",
        "tests/global_overlay",
    ]


def test_mixed_file_list_deduplicates_and_sorts():
    result = run_script(
        "app/global_overlay/overlay_manager.py",
        "app/help/help_window.py",
        "app/global_overlay/watchdog.py",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "tests/architecture/test_gui_domain_dependency_guards.py",
        "tests/architecture/test_gui_governance_guards.py",
        "tests/global_overlay",
        "tests/smoke/test_help_window_smoke.py",
    ]


def test_multiple_central_areas_are_mapped():
    result = run_script(
        "app/core/bootstrap.py",
        "app/chat/streaming.py",
        "app/services/project_service.py",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "tests/architecture/test_chat_domain_governance_guards.py",
        "tests/architecture/test_qml_python_bridge_no_direct_services.py",
        "tests/architecture/test_service_governance_guards.py",
        "tests/architecture/test_startup_governance_guards.py",
        "tests/chat",
        "tests/integration/test_chat_prompt_integration.py",
        "tests/unit",
        "tests/unit/chat",
        "tests/unit/services",
    ]


def test_governance_adjacent_mapping_adds_architecture_tests():
    result = run_script("app/providers/ollama_client.py")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "tests/architecture/test_provider_orchestrator_governance_guards.py",
        "tests/architecture/test_providers_public_surface_guard.py",
        "tests/contracts/test_ollama_response_contract.py",
    ]


def test_duplicate_inputs_and_absolute_paths_are_normalized():
    result = run_script(
        str(ROOT / "app" / "workspace_presets" / "preset_loader.py"),
        "app/workspace_presets/preset_loader.py",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "tests/architecture/test_feature_governance_guards.py",
        "tests/architecture/test_workspace_wiring.py",
        "tests/workspace_presets",
    ]


def test_unknown_file_is_reported_cleanly():
    result = run_script("app/unknown/new_file.py")
    assert result.returncode == 0
    assert result.stdout == ""
    assert "No mapped test scope for: app/unknown/new_file.py" in result.stderr


def test_json_output_includes_unknown_files():
    result = run_script(
        "--format",
        "json",
        "app/ui_application/presenter.py",
        "docs/architecture/overview.md",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_files"] == [
        "app/ui_application/presenter.py",
        "docs/architecture/overview.md",
        "unknown.txt",
    ]
    assert payload["suggested_tests"] == [
        "tests/architecture",
        "tests/architecture/test_presenter_base_usage.py",
        "tests/architecture/test_ui_layer_guardrails.py",
        "tests/unit/ui_application",
    ]
    assert payload["unknown_files"] == ["unknown.txt"]


def test_json_output_handles_scripts_qa_and_release_docs():
    result = run_script(
        "--format",
        "json",
        "scripts/qa/build_coverage_map.py",
        "docs/release/release_notes.md",
        "docs/release_audit/release_readiness.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["suggested_tests"] == [
        "tests/architecture/test_architecture_drift_radar.py",
        "tests/architecture/test_edition_manifest_guards.py",
        "tests/qa",
        "tests/qa/coverage_map",
        "tests/qa/feedback_loop",
        "tests/qa/test_inventory",
    ]
    assert payload["unknown_files"] == []
