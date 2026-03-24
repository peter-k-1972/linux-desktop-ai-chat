# Test inventory — Linux Desktop Chat

**Scope:** Classification of automated tests by directory and by `pytest.ini` markers. Counts are Python files under `tests/`, excluding `__pycache__`, from a `find` pass on 2026-03-24.

**Total:** 532 `*.py` files under `tests/`.

---

## 1. Top-level test directories (file counts)

| Directory | `.py` files |
|-----------|-------------|
| `tests/unit/` | 186 |
| `tests/qa/` | 48 |
| `tests/architecture/` | 47 |
| `tests/smoke/` | 40 |
| `tests/contracts/` | 36 |
| `tests/ui/` | 21 |
| `tests/context/` | 19 |
| `tests/chat/` | 15 |
| `tests/failure_modes/` | 14 |
| `tests/integration/` | 10 |
| `tests/golden_path/` | 9 |
| `tests/tools/` | 7 |
| `tests/helpers/` | 6 |
| `tests/chaos/` | 5 |
| `tests/regression/` | 7 |
| `tests/structure/` | 4 |
| `tests/state_consistency/` | 4 |
| `tests/live/` | 4 |
| `tests/startup/` | 3 |
| `tests/cross_layer/` | 3 |
| `tests/meta/` | 3 |
| `tests/async_behavior/` | 8 |
| `tests/behavior/` | 2 |
| `tests/cli/` | 2 |
| `tests/scripts/` | 1 |
| `tests/data/` | 0 |
| `tests/fixtures/` | 0 |

**Root-level `tests/*.py`:** 28 files (includes `conftest.py`, `qt_ui.py`, and assorted `test_*.py` not in subfolders).

---

## 2. Pytest markers (`pytest.ini`)

Defined markers:

- `unit`, `ui`, `smoke`, `integration`, `live`, `slow`, `golden_path`, `regression`, `async_behavior`, `contract`, `failure_mode`, `cross_layer`, `state_consistency`, `startup`, `chaos`
- CI-oriented: `fast`, `full`, `architecture`
- Special: `context_observability`, `markdown_gate`, `model_usage_gate`

**Note:** A search for `@pytest.mark.context_observability` under `tests/` returned **no matches** (marker exists in config only).

---

## 3. Classification mapping (directory ↔ category)

| Category | Primary locations | Notes |
|----------|-------------------|--------|
| **Unit tests** | `tests/unit/` (incl. `unit/gui`, `unit/services`, `unit/core`, `unit/workflows`, `unit/ui_application`, `unit/adapters`, `unit/ui_runtime`, `unit/agents`, `unit/themes`, `unit/scheduling`), root `tests/test_*.py` | Isolated component tests per layout |
| **Integration tests** | `tests/integration/` | Marker `integration` used in many files across tree per spot checks |
| **Architecture guard tests** | `tests/architecture/` (46 test modules + `arch_guard_config.py`) | Many modules use `@pytest.mark.architecture` |
| **GUI / UI tests** | `tests/ui/` | Marker `ui` in `pytest.ini`; uses Qt patterns per suite naming |
| **Smoke tests** | `tests/smoke/` | Marker `smoke` |
| **Contract tests** | `tests/contracts/` | Marker `contract` |
| **Failure / resiliency** | `tests/failure_modes/` | Marker `failure_mode` |
| **Chaos tests** | `tests/chaos/` | See §4 |
| **Golden path** | `tests/golden_path/` | Marker `golden_path` |
| **Regression** | `tests/regression/` | Marker `regression` |
| **Async behavior** | `tests/async_behavior/` | Marker `async_behavior` |
| **Cross-layer** | `tests/cross_layer/` | Marker `cross_layer` |
| **State consistency** | `tests/state_consistency/` | Marker `state_consistency` |
| **Startup** | `tests/startup/` | Marker `startup` |
| **Live (external deps)** | `tests/live/` | Marker `live` |
| **QA subsystem** | `tests/qa/` (`autopilot_v3/`, `coverage_map/`, `feedback_loop/`, `generators/`, `golden/`, `test_inventory/`) | Mix of unit-style and integration-style modules |
| **Context / explainability** | `tests/context/`, `tests/chat/` (context policy tests) | Overlaps with observability themes; no `context_observability` marks found |
| **Tools / meta** | `tests/tools/`, `tests/meta/` | Guards and tooling tests |
| **CLI** | `tests/cli/` | Includes replay CLI test (see §5) |
| **Behavior** | `tests/behavior/` | Small suite |

---

## 4. Chaos tests (`tests/chaos/`)

Files:

- `test_embedding_service_unreachable.py` — `@pytest.mark.chaos` (multiple tests)
- `test_persistence_failure_after_success.py` — `@pytest.mark.chaos`
- `test_provider_timeout_chat.py` — `@pytest.mark.chaos`
- `test_startup_partial_services.py` — `@pytest.mark.chaos`

---

## 5. Replay- and incident-related tests (by path name / registry)

Referenced explicitly for **Replay Lab** in `docs/FEATURE_REGISTRY.md`:

- `tests/cli/test_context_replay_cli.py`
- `tests/context/test_context_replay.py`
- `tests/qa/test_enrich_replay_binding.py`

Additional tests whose paths mention replay / incident / repro (non-exhaustive grep for `replay|incident` in path or filename under `tests/`):

- `tests/context/test_repro_case_pipeline.py`
- `tests/helpers/repro_failure_helper.py`, `tests/helpers/test_repro_failure_helper.py`
- `tests/unit/services/test_incident_service.py`
- `tests/unit/gui/test_audit_incidents_workspace.py`
- `tests/unit/core/audit/test_audit_incident_repository.py`
- Multiple `tests/qa/feedback_loop/*` and `tests/qa/autopilot_v3/*` files referencing incidents/backlog in filenames or imports (see repository search results).

---

## 6. Architecture test module list (`tests/architecture/`)

`test_agent_registry_panel_guardrails.py`, `test_agent_tasks_inspector_guardrails.py`, `test_agent_tasks_workspace_guardrails.py`, `test_agent_tasks_workspace_runtime_guardrails.py`, `test_app_package_guards.py`, `test_architecture_drift_radar.py`, `test_architecture_graph.py`, `test_architecture_health_check.py`, `test_architecture_map.py`, `test_architecture_map_contract.py`, `test_command_dispatcher_usage.py`, `test_deployment_edit_dialogs_project_service_guardrails.py`, `test_deployment_releases_panel_guardrails.py`, `test_deployment_rollouts_panel_guardrails.py`, `test_deployment_targets_panel_guardrails.py`, `test_eventbus_governance_guards.py`, `test_feature_governance_guards.py`, `test_gui_domain_dependency_guards.py`, `test_gui_does_not_import_ui.py`, `test_gui_governance_guards.py`, `test_lifecycle_guards.py`, `test_model_settings_panel_guardrails.py`, `test_presenter_base_usage.py`, `test_project_category_guardrails.py`, `test_prompt_detail_guardrails.py`, `test_prompt_library_panel_guardrails.py`, `test_prompt_list_panel_guardrails.py`, `test_prompt_studio_remaining_panels_guardrails.py`, `test_prompt_templates_panel_guardrails.py`, `test_prompt_test_lab_panel_guardrails.py`, `test_prompt_version_panel_guardrails.py`, `test_provider_orchestrator_governance_guards.py`, `test_registry_governance_guards.py`, `test_remediation_cc_agents.py`, `test_rollout_record_dialog_guardrails.py`, `test_root_entrypoint_guards.py`, `test_service_governance_guards.py`, `test_settings_ai_models_catalog_guardrails.py`, `test_settings_data_advanced_panel_guardrails.py`, `test_settings_dialog_guardrails.py`, `test_startup_governance_guards.py`, `test_theme_modules_guardrails.py`, `test_theme_selection_panel_guardrails.py`, `test_ui_layer_guardrails.py`, `test_workspace_wiring.py`, plus `arch_guard_config.py`, `__init__.py`.

---

## 7. `tests/qa/` subtree

- `tests/qa/autopilot_v3/` — autopilot v3 tests  
- `tests/qa/coverage_map/` — coverage map aggregation, gaps, governance, loader, strength, prioritization  
- `tests/qa/feedback_loop/` — feedback loop, projections, traces, rules, normalizer, determinism, robustness, etc.  
- `tests/qa/generators/` — generator CLI and update scripts tests  
- `tests/qa/golden/` — golden snapshots (`expected/` present)  
- `tests/qa/test_inventory/` — inventory happy path, rules, governance  
