# Trace Map – Linux Desktop Chat

*Auto-generated: 2026-03-16 14:32*

Run `python tools/generate_trace_map.py` to regenerate.

Connects: **Workspace** → **Code** → **Services** → **Help** → **Tests** → **QA/audits**

---

## 1. Workspace → Code

| Workspace | Code Path |
|-----------|-----------|
| control_center/agents_workspace | `app/gui/domains/control_center/workspaces/agents_workspace.py` |
| control_center/models_workspace | `app/gui/domains/control_center/workspaces/models_workspace.py` |
| control_center/base_management_workspace | `app/gui/domains/control_center/workspaces/base_management_workspace.py` |
| control_center/tools_workspace | `app/gui/domains/control_center/workspaces/tools_workspace.py` |
| control_center/providers_workspace | `app/gui/domains/control_center/workspaces/providers_workspace.py` |
| control_center/data_stores_workspace | `app/gui/domains/control_center/workspaces/data_stores_workspace.py` |
| control_center/panels | `app/gui/domains/control_center/panels/agents_panels.py` |
| control_center/panels | `app/gui/domains/control_center/panels/data_stores_panels.py` |
| control_center/panels | `app/gui/domains/control_center/panels/models_panels.py` |
| control_center/panels | `app/gui/domains/control_center/panels/providers_panels.py` |
| control_center/panels | `app/gui/domains/control_center/panels/tools_panels.py` |
| dashboard/panels | `app/gui/domains/dashboard/panels/active_work_panel.py` |
| dashboard/panels | `app/gui/domains/dashboard/panels/incidents_panel.py` |
| dashboard/panels | `app/gui/domains/dashboard/panels/qa_status_panel.py` |
| dashboard/panels | `app/gui/domains/dashboard/panels/system_status_panel.py` |
| operations/agent_tasks | `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` |
| operations/chat | `app/gui/domains/operations/chat/chat_workspace.py` |
| operations/knowledge | `app/gui/domains/operations/knowledge/knowledge_workspace.py` |
| operations/projects | `app/gui/domains/operations/projects/projects_workspace.py` |
| operations/prompt_studio | `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` |
| qa_governance/replay_lab_workspace | `app/gui/domains/qa_governance/workspaces/replay_lab_workspace.py` |
| qa_governance/gap_analysis_workspace | `app/gui/domains/qa_governance/workspaces/gap_analysis_workspace.py` |
| qa_governance/incidents_workspace | `app/gui/domains/qa_governance/workspaces/incidents_workspace.py` |
| qa_governance/coverage_map_workspace | `app/gui/domains/qa_governance/workspaces/coverage_map_workspace.py` |
| qa_governance/base_analysis_workspace | `app/gui/domains/qa_governance/workspaces/base_analysis_workspace.py` |
| qa_governance/test_inventory_workspace | `app/gui/domains/qa_governance/workspaces/test_inventory_workspace.py` |
| qa_governance/panels | `app/gui/domains/qa_governance/panels/coverage_map_panels.py` |
| qa_governance/panels | `app/gui/domains/qa_governance/panels/gap_analysis_panels.py` |
| qa_governance/panels | `app/gui/domains/qa_governance/panels/incidents_panels.py` |
| qa_governance/panels | `app/gui/domains/qa_governance/panels/replay_lab_panels.py` |
| qa_governance/panels | `app/gui/domains/qa_governance/panels/test_inventory_panels.py` |
| runtime_debug/agent_activity_workspace | `app/gui/domains/runtime_debug/workspaces/agent_activity_workspace.py` |
| runtime_debug/base_monitoring_workspace | `app/gui/domains/runtime_debug/workspaces/base_monitoring_workspace.py` |
| runtime_debug/logs_workspace | `app/gui/domains/runtime_debug/workspaces/logs_workspace.py` |
| runtime_debug/metrics_workspace | `app/gui/domains/runtime_debug/workspaces/metrics_workspace.py` |
| runtime_debug/system_graph_workspace | `app/gui/domains/runtime_debug/workspaces/system_graph_workspace.py` |
| runtime_debug/llm_calls_workspace | `app/gui/domains/runtime_debug/workspaces/llm_calls_workspace.py` |
| runtime_debug/eventbus_workspace | `app/gui/domains/runtime_debug/workspaces/eventbus_workspace.py` |
| runtime_debug/panels | `app/gui/domains/runtime_debug/panels/activity_detail_panel.py` |
| runtime_debug/panels | `app/gui/domains/runtime_debug/panels/agent_activity_panels.py` |
| ... | (14 more) |

## 2. Services

- `app/services/agent_service.py`
- `app/services/chat_service.py`
- `app/services/infrastructure.py`
- `app/services/knowledge_service.py`
- `app/services/model_service.py`
- `app/services/project_service.py`
- `app/services/provider_service.py`
- `app/services/qa_governance_service.py`
- `app/services/result.py`
- `app/services/topic_service.py`

## 3. Workspace → Help

| Workspace | Help Topic |
|-----------|------------|
| `cc_agents` | `control_center_agents` |
| `cc_data_stores` | `cc_data_stores` |
| `cc_models` | `cc_models` |
| `cc_providers` | `cc_providers` |
| `cc_tools` | `cc_tools` |
| `operations_agent_tasks` | `agents_overview` |
| `operations_chat` | `chat_overview` |
| `operations_knowledge` | `knowledge_overview` |
| `operations_projects` | `projects_overview` |
| `operations_prompt_studio` | `prompt_studio_overview` |
| `qa_test_inventory` | `qa_overview` |
| `rd_logs` | `runtime_overview` |
| `settings_appearance` | `settings_overview` |

## 4. Help Topics

- `help/control_center/cc_data_stores.md`
- `help/control_center/cc_models.md`
- `help/control_center/cc_providers.md`
- `help/control_center/cc_tools.md`
- `help/control_center/control_center_agents.md`
- `help/control_center/control_center_overview.md`
- `help/getting_started/introduction.md`
- `help/operations/agents_overview.md`
- `help/operations/chat_overview.md`
- `help/operations/knowledge_overview.md`
- `help/operations/projects_overview.md`
- `help/operations/prompt_studio_overview.md`
- `help/qa_governance/qa_overview.md`
- `help/runtime_debug/runtime_overview.md`
- `help/settings/settings_overview.md`
- `help/settings/settings_prompts.md`
- `help/settings/settings_rag.md`
- `help/troubleshooting/troubleshooting.md`

## 5. Test Suites

- `tests/qa/` — 36 test modules
- `tests/failure_modes/` — 12 test modules
- `tests/contracts/` — 8 test modules
- `tests/integration/` — 8 test modules
- `tests/ui/` — 8 test modules
- `tests/golden_path/` — 7 test modules
- `tests/async_behavior/` — 6 test modules
- `tests/unit/` — 6 test modules
- `tests/regression/` — 5 test modules
- `tests/smoke/` — 5 test modules
- `tests/chaos/` — 4 test modules
- `tests/live/` — 3 test modules
- `tests/state_consistency/` — 3 test modules
- `tests/cross_layer/` — 2 test modules
- `tests/meta/` — 2 test modules
- `tests/startup/` — 2 test modules
- `tests/helpers/` — 1 test modules

## 6. QA / Audits (docs/qa)

- `docs/qa/ARCHITECTURE_DRIFT_SENTINELS.md`
- `docs/qa/CHAOS_QA_PLAN.md`
- `docs/qa/CI_TEST_LEVELS.md`
- `docs/qa/FEEDBACK_LOOP_REPORT.json`
- `docs/qa/PHASE3_CI_INTEGRATION_PLAN.md`
- `docs/qa/PHASE3_GAP_PRIORITIZATION.md`
- `docs/qa/PHASE3_GAP_REPORT.json`
- `docs/qa/PHASE3_GAP_REPORT.md`
- `docs/qa/PHASE3_IMPLEMENTATION_REPORT.md`
- `docs/qa/PHASE3_ORPHAN_REVIEW_GOVERNANCE.md`
- `docs/qa/PHASE3_REPLAY_BINDING_ARCHITECTURE.md`
- `docs/qa/PHASE3_RESTRISIKEN_REPORT.md`
- `docs/qa/PHASE3_SEMANTIC_ENRICHMENT_PLAN.md`
- `docs/qa/PHASE3_SUMMARY.md`
- `docs/qa/PHASE3_TECHNICAL_DOCS.md`
- `docs/qa/PHASE3_VERIFICATION_REVIEW.md`
- `docs/qa/QA_ANOMALY_DETECTION.json`
- `docs/qa/QA_ANOMALY_DETECTION.md`
- `docs/qa/QA_ARCHITECTURE_GRAPH.md`
- `docs/qa/QA_AUTOPILOT.json`
- `docs/qa/QA_AUTOPILOT.md`
- `docs/qa/QA_AUTOPILOT_V2.json`
- `docs/qa/QA_AUTOPILOT_V2_ARCHITECTURE.md`
- `docs/qa/QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md`
- `docs/qa/QA_AUTOPILOT_V3.json`
- `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md`
- `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE_REVIEW.md`
- `docs/qa/QA_AUTOPILOT_V3_CHANGE_SUMMARY.md`
- `docs/qa/QA_AUTOPILOT_V3_FINAL_RELEASE_CHECK.md`
- `docs/qa/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md`
