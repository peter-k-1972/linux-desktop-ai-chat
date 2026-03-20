# Feature Registry – Linux Desktop Chat

*Auto-generated: 2026-03-16 19:40*

Run `python3 tools/generate_feature_registry.py` to regenerate.

System-wide index of features and their implementation. Each feature references:
- **Workspace** | **Code modules** | **Services** | **Help articles** | **Tests** | **QA documentation**

---

## Operations

### Chat

| Attribute | Value |
|-----------|-------|
| Workspace | `operations_chat` |
| Code | `app/gui/domains/operations/chat/chat_workspace.py` |
| Services | `chat_service`, `llm`, `model_service`, `provider_service` |
| Help | `chat_overview` |
| Tests | `tests/async_behavior/test_chatwidget_signal_after_destroy.py`, `tests/chaos/test_provider_timeout_chat.py`, `tests/contracts/test_chat_event_contract.py`, `tests/failure_modes/test_metrics_on_failed_chat_or_task.py`, `tests/golden_path/test_agent_in_chat_golden_path.py` (+5 more) |
| QA docs | — |

### Knowledge

| Attribute | Value |
|-----------|-------|
| Workspace | `operations_knowledge` |
| Code | `app/gui/domains/operations/knowledge/knowledge_workspace.py` |
| Services | `knowledge_service`, `rag` |
| Help | `knowledge_overview` |
| Tests | `tests/async_behavior/test_rag_concurrent_retrieval.py`, `tests/chaos/test_embedding_service_unreachable.py`, `tests/contracts/test_rag_retrieval_contract.py`, `tests/failure_modes/test_rag_empty_results.py`, `tests/failure_modes/test_rag_retrieval_failure.py` (+5 more) |
| QA docs | — |

### Prompt Studio

| Attribute | Value |
|-----------|-------|
| Workspace | `operations_prompt_studio` |
| Code | `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` |
| Services | `prompts`, `topic_service` |
| Help | `prompt_studio_overview` |
| Tests | `tests/contracts/test_prompt_contract.py`, `tests/cross_layer/test_prompt_apply_affects_real_request.py`, `tests/failure_modes/test_prompt_service_failure.py`, `tests/golden_path/test_prompt_golden_path.py`, `tests/integration/test_chat_prompt_integration.py` (+4 more) |
| QA docs | — |

### Agent Tasks

| Attribute | Value |
|-----------|-------|
| Workspace | `operations_agent_tasks` |
| Code | `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` |
| Services | `agent_service`, `agents` |
| Help | `agents_overview` |
| Tests | `tests/async_behavior/test_agent_change_during_stream.py`, `tests/contracts/test_agent_profile_contract.py`, `tests/golden_path/test_agent_golden_path.py`, `tests/golden_path/test_agent_in_chat_golden_path.py`, `tests/live/test_agent_execution.py` (+5 more) |
| QA docs | — |

### Projects

| Attribute | Value |
|-----------|-------|
| Workspace | `operations_projects` |
| Code | `app/gui/domains/operations/projects/projects_workspace.py` |
| Services | `project_service` |
| Help | `projects_overview` |
| Tests | `tests/qa/feedback_loop/test_projections.py`, `tests/regression/test_chat_without_project.py`, `tests/test_projects.py` |
| QA docs | — |

## Control Center

### Models

| Attribute | Value |
|-----------|-------|
| Workspace | `cc_models` |
| Code | `app/gui/domains/control_center/workspaces/models_workspace.py` |
| Services | `model_service`, `provider_service` |
| Help | `cc_models` |
| Tests | `tests/chaos/test_provider_timeout_chat.py`, `tests/integration/test_model_settings_chat.py`, `tests/test_model_router.py`, `tests/test_model_settings_bindings.py` |
| QA docs | — |

### Providers

| Attribute | Value |
|-----------|-------|
| Workspace | `cc_providers` |
| Code | `app/gui/domains/control_center/workspaces/providers_workspace.py` |
| Services | `provider_service` |
| Help | `cc_providers` |
| Tests | `tests/chaos/test_provider_timeout_chat.py` |
| QA docs | — |

### Agents

| Attribute | Value |
|-----------|-------|
| Workspace | `cc_agents` |
| Code | `app/gui/domains/control_center/workspaces/agents_workspace.py` |
| Services | `agent_service`, `agents` |
| Help | `control_center_agents` |
| Tests | `tests/async_behavior/test_agent_change_during_stream.py`, `tests/contracts/test_agent_profile_contract.py`, `tests/golden_path/test_agent_golden_path.py`, `tests/golden_path/test_agent_in_chat_golden_path.py`, `tests/live/test_agent_execution.py` (+5 more) |
| QA docs | — |

### Tools

| Attribute | Value |
|-----------|-------|
| Workspace | `cc_tools` |
| Code | `app/gui/domains/control_center/workspaces/tools_workspace.py` |
| Services | — |
| Help | `cc_tools` |
| Tests | `tests/contracts/test_tool_result_contract.py`, `tests/failure_modes/test_tool_failure.py`, `tests/test_tools_execute_command.py`, `tests/test_tools_workspace_paths.py`, `tests/unit/test_tools.py` |
| QA docs | — |

### Data Stores

| Attribute | Value |
|-----------|-------|
| Workspace | `cc_data_stores` |
| Code | `app/gui/domains/control_center/workspaces/data_stores_workspace.py` |
| Services | `rag` |
| Help | `cc_data_stores` |
| Tests | `tests/async_behavior/test_rag_concurrent_retrieval.py`, `tests/contracts/test_rag_retrieval_contract.py`, `tests/failure_modes/test_chroma_import_failure.py`, `tests/failure_modes/test_chroma_unreachable.py`, `tests/failure_modes/test_rag_empty_results.py` (+5 more) |
| QA docs | — |

## QA & Governance

### Test Inventory

| Attribute | Value |
|-----------|-------|
| Workspace | `qa_test_inventory` |
| Code | `app/gui/domains/qa_governance/workspaces/test_inventory_workspace.py` |
| Services | `qa_governance_service` |
| Help | `qa_overview` |
| Tests | `tests/qa/coverage_map/test_coverage_map_aggregation.py`, `tests/qa/coverage_map/test_coverage_map_gaps.py`, `tests/qa/coverage_map/test_coverage_map_governance.py`, `tests/qa/coverage_map/test_coverage_map_loader.py`, `tests/qa/coverage_map/test_coverage_map_strength.py` (+4 more) |
| QA docs | `docs/qa/00_map_of_qa_system.md`, `docs/qa/README.md`, `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md` |

### Coverage Map

| Attribute | Value |
|-----------|-------|
| Workspace | `qa_coverage_map` |
| Code | `app/gui/domains/qa_governance/workspaces/coverage_map_workspace.py` |
| Services | `qa_governance_service` |
| Help | — |
| Tests | `tests/qa/coverage_map/test_coverage_map_aggregation.py`, `tests/qa/coverage_map/test_coverage_map_gaps.py`, `tests/qa/coverage_map/test_coverage_map_governance.py`, `tests/qa/coverage_map/test_coverage_map_loader.py`, `tests/qa/coverage_map/test_coverage_map_strength.py` |
| QA docs | `docs/qa/00_map_of_qa_system.md`, `docs/qa/README.md`, `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md` |

### Gap Analysis

| Attribute | Value |
|-----------|-------|
| Workspace | `qa_gap_analysis` |
| Code | `app/gui/domains/qa_governance/workspaces/gap_analysis_workspace.py` |
| Services | `qa_governance_service` |
| Help | — |
| Tests | `tests/qa/autopilot_v3/test_gap_detection.py`, `tests/qa/autopilot_v3/test_translation_gaps.py`, `tests/qa/coverage_map/test_coverage_map_gaps.py`, `tests/qa/coverage_map/test_gap_prioritization.py` |
| QA docs | `docs/qa/00_map_of_qa_system.md`, `docs/qa/README.md`, `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md` |

### Incidents

| Attribute | Value |
|-----------|-------|
| Workspace | `qa_incidents` |
| Code | `app/gui/domains/qa_governance/workspaces/incidents_workspace.py` |
| Services | `qa_governance_service` |
| Help | — |
| Tests | — |
| QA docs | `docs/qa/00_map_of_qa_system.md`, `docs/qa/README.md`, `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md` |

### Replay Lab

| Attribute | Value |
|-----------|-------|
| Workspace | `qa_replay_lab` |
| Code | `app/gui/domains/qa_governance/workspaces/replay_lab_workspace.py` |
| Services | `qa_governance_service` |
| Help | — |
| Tests | `tests/qa/test_enrich_replay_binding.py` |
| QA docs | `docs/qa/00_map_of_qa_system.md`, `docs/qa/README.md`, `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md` |

## Runtime / Debug

### EventBus

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_eventbus` |
| Code | `app/gui/domains/runtime_debug/workspaces/eventbus_workspace.py` |
| Services | — |
| Help | — |
| Tests | `tests/contracts/test_chat_event_contract.py`, `tests/contracts/test_debug_event_contract.py`, `tests/cross_layer/test_debug_view_matches_failure_events.py`, `tests/failure_modes/test_event_bus_listener_error.py`, `tests/failure_modes/test_event_store_failure.py` (+2 more) |
| QA docs | — |

### Logs

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_logs` |
| Code | `app/gui/domains/runtime_debug/workspaces/logs_workspace.py` |
| Services | — |
| Help | `runtime_overview` |
| Tests | `tests/qa/autopilot_v3/test_backlog.py`, `tests/test_streaming_logic.py` |
| QA docs | — |

### Metrics

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_metrics` |
| Code | `app/gui/domains/runtime_debug/workspaces/metrics_workspace.py` |
| Services | — |
| Help | — |
| Tests | `tests/failure_modes/test_metrics_on_failed_chat_or_task.py`, `tests/test_metrics.py`, `tests/unit/test_metrics.py` |
| QA docs | — |

### LLM Calls

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_llm_calls` |
| Code | `app/gui/domains/runtime_debug/workspaces/llm_calls_workspace.py` |
| Services | — |
| Help | — |
| Tests | `tests/contracts/test_llm_stream_contract.py`, `tests/failure_modes/test_llm_chunk_parsing_failure.py`, `tests/qa/feedback_loop/test_traces.py`, `tests/test_llm_output_pipeline.py` |
| QA docs | — |

### Agent Activity

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_agent_activity` |
| Code | `app/gui/domains/runtime_debug/workspaces/agent_activity_workspace.py` |
| Services | `agent_service` |
| Help | — |
| Tests | — |
| QA docs | — |

### System Graph

| Attribute | Value |
|-----------|-------|
| Workspace | `rd_system_graph` |
| Code | `app/gui/domains/runtime_debug/workspaces/system_graph_workspace.py` |
| Services | — |
| Help | — |
| Tests | — |
| QA docs | — |

## Settings

### Application

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_application` |
| Code | `app/gui/domains/settings/categories/application_category.py`, `app/gui/domains/settings/workspaces/system_workspace.py` |
| Services | `infrastructure` |
| Help | — |
| Tests | `tests/chaos/test_startup_partial_services.py`, `tests/integration/test_model_settings_chat.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/smoke/test_app_startup.py`, `tests/startup/test_startup_without_ollama.py` (+1 more) |
| QA docs | — |

### Appearance

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_appearance` |
| Code | `app/gui/domains/settings/categories/appearance_category.py`, `app/gui/domains/settings/workspaces/appearance_workspace.py` |
| Services | — |
| Help | `settings_overview` |
| Tests | `tests/regression/test_settings_theme_tokens.py` |
| QA docs | — |

### AI / Models

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_ai_models` |
| Code | `app/gui/domains/settings/categories/ai_models_category.py`, `app/gui/domains/settings/workspaces/models_workspace.py` |
| Services | `model_service`, `provider_service` |
| Help | — |
| Tests | `tests/integration/test_model_settings_chat.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/test_model_router.py`, `tests/test_model_settings_bindings.py` |
| QA docs | — |

### Data

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_data` |
| Code | `app/gui/domains/settings/categories/data_category.py` |
| Services | `rag` |
| Help | — |
| Tests | `tests/integration/test_model_settings_chat.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/test_model_settings_bindings.py` |
| QA docs | — |

### Privacy

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_privacy` |
| Code | `app/gui/domains/settings/categories/privacy_category.py` |
| Services | — |
| Help | — |
| Tests | — |
| QA docs | — |

### Advanced

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_advanced` |
| Code | `app/gui/domains/settings/categories/advanced_category.py`, `app/gui/domains/settings/workspaces/advanced_workspace.py` |
| Services | — |
| Help | — |
| Tests | `tests/integration/test_model_settings_chat.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/test_model_settings_bindings.py` |
| QA docs | — |

### Project

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_project` |
| Code | `app/gui/domains/settings/categories/project_category.py` |
| Services | `project_service` |
| Help | — |
| Tests | `tests/integration/test_model_settings_chat.py`, `tests/qa/feedback_loop/test_projections.py`, `tests/regression/test_chat_without_project.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/test_model_settings_bindings.py` (+1 more) |
| QA docs | — |

### Workspace

| Attribute | Value |
|-----------|-------|
| Workspace | `settings_workspace` |
| Code | `app/gui/domains/settings/categories/workspace_category.py` |
| Services | — |
| Help | — |
| Tests | `tests/integration/test_model_settings_chat.py`, `tests/regression/test_settings_theme_tokens.py`, `tests/test_model_settings_bindings.py`, `tests/test_tools_workspace_paths.py` |
| QA docs | — |

---

## Related Documents

- [00_map_of_the_system.md](00_map_of_the_system.md) — Human-readable orientation
- [SYSTEM_MAP.md](SYSTEM_MAP.md) — Structural map
- [TRACE_MAP.md](TRACE_MAP.md) — Code/help/test traceability
