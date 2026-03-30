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
    assert "unknown_file_details" not in payload
    assert "stats" not in payload
    assert "match_details" not in payload
    assert "file_targets" not in payload
    assert "match_counts" not in payload
    assert "pattern_summary" not in payload


def test_json_output_include_unknown_adds_structured_details():
    result = run_script(
        "--format",
        "json",
        "--include-unknown",
        "app/chat/streaming.py",
        "unknown.txt",
        "app/not_mapped/file.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["suggested_tests"] == [
        "tests/architecture/test_chat_domain_governance_guards.py",
        "tests/chat",
        "tests/integration/test_chat_prompt_integration.py",
        "tests/unit/chat",
    ]
    assert payload["unknown_files"] == [
        "unknown.txt",
        "app/not_mapped/file.py",
    ]
    assert payload["unknown_file_details"] == [
        {
            "path": "unknown.txt",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        },
        {
            "path": "app/not_mapped/file.py",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        },
    ]


def test_json_output_include_stats_adds_mapped_and_unmapped_counts():
    result = run_script(
        "--format",
        "json",
        "--include-stats",
        "app/chat/streaming.py",
        "unknown.txt",
        "app/providers/ollama_client.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["unknown_files"] == ["unknown.txt"]
    assert payload["stats"] == {
        "total_files": 3,
        "mapped_files": 2,
        "unmapped_files": 1,
    }


def test_json_output_include_match_details_shows_patterns_per_file():
    result = run_script(
        "--format",
        "json",
        "--include-match-details",
        "app/chat/streaming.py",
        "app/providers/ollama_client.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["match_details"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "matched_patterns": ["app/chat/**"],
        },
        {
            "path": "app/providers/ollama_client.py",
            "matched": True,
            "matched_patterns": ["app/providers/**"],
        },
    ]


def test_json_output_include_file_targets_shows_test_targets_per_file():
    result = run_script(
        "--format",
        "json",
        "--include-file-targets",
        "app/chat/streaming.py",
        "app/providers/ollama_client.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["file_targets"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "test_targets": [
                "tests/architecture/test_chat_domain_governance_guards.py",
                "tests/chat",
                "tests/integration/test_chat_prompt_integration.py",
                "tests/unit/chat",
            ],
        },
        {
            "path": "app/providers/ollama_client.py",
            "matched": True,
            "test_targets": [
                "tests/architecture/test_provider_orchestrator_governance_guards.py",
                "tests/architecture/test_providers_public_surface_guard.py",
                "tests/contracts/test_ollama_response_contract.py",
            ],
        },
    ]


def test_json_output_include_match_counts_shows_mapping_entry_counts_per_file():
    result = run_script(
        "--format",
        "json",
        "--include-match-counts",
        "app/chat/streaming.py",
        "app/providers/ollama_client.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["match_counts"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "match_count": 1,
        },
        {
            "path": "app/providers/ollama_client.py",
            "matched": True,
            "match_count": 1,
        },
        {
            "path": "unknown.txt",
            "matched": False,
            "match_count": 0,
        },
    ]


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


def test_json_output_can_combine_include_unknown_and_stats():
    result = run_script(
        "--format",
        "json",
        "--include-unknown",
        "--include-stats",
        "app/chat/streaming.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["unknown_file_details"] == [
        {
            "path": "unknown.txt",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        }
    ]
    assert payload["stats"] == {
        "total_files": 2,
        "mapped_files": 1,
        "unmapped_files": 1,
    }


def test_json_output_can_combine_match_details_unknown_and_stats():
    result = run_script(
        "--format",
        "json",
        "--include-match-details",
        "--include-unknown",
        "--include-stats",
        "app/chat/streaming.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["match_details"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "matched_patterns": ["app/chat/**"],
        },
        {
            "path": "unknown.txt",
            "matched": False,
            "matched_patterns": [],
        },
    ]
    assert payload["unknown_file_details"] == [
        {
            "path": "unknown.txt",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        }
    ]
    assert payload["stats"] == {
        "total_files": 2,
        "mapped_files": 1,
        "unmapped_files": 1,
    }


def test_json_output_can_combine_file_targets_with_other_json_options():
    result = run_script(
        "--format",
        "json",
        "--include-file-targets",
        "--include-match-details",
        "--include-unknown",
        "--include-stats",
        "app/chat/streaming.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["file_targets"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "test_targets": [
                "tests/architecture/test_chat_domain_governance_guards.py",
                "tests/chat",
                "tests/integration/test_chat_prompt_integration.py",
                "tests/unit/chat",
            ],
        },
        {
            "path": "unknown.txt",
            "matched": False,
            "test_targets": [],
        },
    ]
    assert payload["match_details"][1] == {
        "path": "unknown.txt",
        "matched": False,
        "matched_patterns": [],
    }
    assert payload["unknown_file_details"] == [
        {
            "path": "unknown.txt",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        }
    ]
    assert payload["stats"] == {
        "total_files": 2,
        "mapped_files": 1,
        "unmapped_files": 1,
    }


def test_json_output_can_combine_match_counts_with_existing_json_options():
    result = run_script(
        "--format",
        "json",
        "--include-match-counts",
        "--include-file-targets",
        "--include-match-details",
        "--include-unknown",
        "--include-stats",
        "app/chat/streaming.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["match_counts"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "match_count": 1,
        },
        {
            "path": "unknown.txt",
            "matched": False,
            "match_count": 0,
        },
    ]
    assert payload["match_details"][0]["matched_patterns"] == ["app/chat/**"]
    assert payload["file_targets"][1] == {
        "path": "unknown.txt",
        "matched": False,
        "test_targets": [],
    }
    assert payload["unknown_file_details"] == [
        {
            "path": "unknown.txt",
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        }
    ]
    assert payload["stats"] == {
        "total_files": 2,
        "mapped_files": 1,
        "unmapped_files": 1,
    }


def test_json_output_pattern_summary_shows_hit_counts_across_inputs():
    result = run_script(
        "--format",
        "json",
        "--pattern-summary",
        "app/chat/streaming.py",
        "app/chat/history.py",
        "app/providers/ollama_client.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pattern_summary"] == [
        {
            "pattern": "app/chat/**",
            "hit_count": 2,
        },
        {
            "pattern": "app/providers/**",
            "hit_count": 1,
        },
    ]


def test_json_output_can_combine_pattern_summary_with_other_json_options():
    result = run_script(
        "--format",
        "json",
        "--pattern-summary",
        "--include-match-counts",
        "--include-match-details",
        "--include-file-targets",
        "--include-unknown",
        "--include-stats",
        "app/chat/streaming.py",
        "app/chat/history.py",
        "unknown.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pattern_summary"] == [
        {
            "pattern": "app/chat/**",
            "hit_count": 2,
        }
    ]
    assert payload["match_counts"] == [
        {
            "path": "app/chat/streaming.py",
            "matched": True,
            "match_count": 1,
        },
        {
            "path": "app/chat/history.py",
            "matched": True,
            "match_count": 1,
        },
        {
            "path": "unknown.txt",
            "matched": False,
            "match_count": 0,
        },
    ]
    assert payload["stats"] == {
        "total_files": 3,
        "mapped_files": 2,
        "unmapped_files": 1,
    }
