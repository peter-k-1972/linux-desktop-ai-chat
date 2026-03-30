# System Map – Linux Desktop Chat

*Auto-generated: 2026-03-30 21:30*

Run `python3 tools/generate_system_map.py` to regenerate.

---

## Top-Level Layout

```
  app/
  docs/
  help/
  tests/
  scripts/
  tools/
  assets/
  archive/
  examples/
  static/
```

## Application Structure

```
  app/agents/
  app/application_release_info.py
  app/chat/
  app/chats/
  linux-desktop-chat-cli/src/app/cli/   # Import app.cli
  app/cli/
  app/commands/
  app/context/
  app/core/
  app/critic.py
  app/devtools/
  app/diagnostics/
  app/domain/
  app/global_overlay/
  app/gui/
  app/gui_designer_dummy/
  app/gui_smoke_constants.py
  app/gui_smoke_harness.py
  app/help/
  app/llm/
  app/main.py
  app/packaging/
  app/persistence/
  app/plugins/
  linux-desktop-chat-projects/src/app/projects/   # Import app.projects
  linux-desktop-chat-workflows/src/app/workflows/   # Import app.workflows
  app/prompts/
  app/qa/
  app/qml_alternative_gui_validator.py
  app/qml_theme_governance.py
  app/rag/
  app/resources/
  app/resources_rc.py
  app/services/
  app/ui_application/
  app/utils/
  app/workspace_presets/
```

## Workspaces

### Command Center


### Control Center

- Screen: ControlCenterScreen
-   Workspace: AgentsWorkspace
-   Workspace: DataStoresWorkspace
-   Workspace: ModelsWorkspace
-   Workspace: ProvidersWorkspace
-   Workspace: ToolsWorkspace

### Dashboard

- Screen: DashboardScreen

### Debug


### Operations

- Screen: OperationsScreen
-   Workspace: AgentTasksWorkspace (agent_tasks)
-   Workspace: AuditIncidentsWorkspace (audit_incidents)
-   Workspace: ChatWorkspaceChatSink (chat)
-   Workspace: ChatWorkspace (chat)
-   Workspace: DeploymentWorkspace (deployment)
-   Workspace: KnowledgeWorkspace (knowledge)
-   Workspace: ProjectsWorkspace (projects)
-   Workspace: PromptStudioWorkspace (prompt_studio)
-   Workspace: WorkflowsWorkspace (workflows)

### Project Hub


### Prompt Studio


### Qa Governance

- Screen: QAGovernanceScreen
-   Workspace: CoverageMapWorkspace
-   Workspace: GapAnalysisWorkspace
-   Workspace: IncidentsWorkspace
-   Workspace: ReplayLabWorkspace
-   Workspace: TestInventoryWorkspace

### Runtime Debug

- Screen: RuntimeDebugScreen
-   Workspace: AgentActivityWorkspace
-   Workspace: EventBusWorkspace
-   Workspace: IntrospectionWorkspace
-   Workspace: LLMCallsWorkspace
-   Workspace: LogsWorkspace
-   Workspace: MetricsWorkspace
-   Workspace: QACockpitWorkspace
-   Workspace: QAObservabilityWorkspace
-   Workspace: SystemGraphWorkspace

### Settings

- Screen: SettingsScreen
-   Workspace: AdvancedWorkspace
-   Workspace: AgentsWorkspace
-   Workspace: AppearanceWorkspace
-   Workspace: ModelsWorkspace
-   Workspace: SystemWorkspace
-   Workspace: WorkspaceCategory (categories)

## Services

- `agent_operations_read_service`
- `agent_service`
- `agents`
- `audit_service`
- `chat_service`
- `context_explain_service`
- `context_inspection_service`
- `deployment_operations_service`
- `doc_search_service`
- `incident_service`
- `infrastructure`
- `infrastructure_snapshot`
- `knowledge_service`
- `llm`
- `local_model_asset_classifier`
- `local_model_default_roots`
- `local_model_matcher`
- `local_model_registry_service`
- `local_model_scanner_service`
- `model_chat_runtime`
- `model_invocation_display`
- `model_orchestrator_service`
- `model_quota_service`
- `model_service`
- `model_usage_aggregation_service`
- `model_usage_gui_service`
- `model_usage_service`
- `pipeline_service`
- `platform_health_service`
- `project_butler_service`
- `project_service`
- `prompts`
- `provider_service`
- `provider_usage_normalizer`
- `qa_governance_service`
- `rag`
- `result`
- `schedule_service`
- `token_usage_estimation`
- `topic_service`
- `unified_model_catalog_service`
- `workflow_agent_adapter`
- `workflow_context_adapter`
- `workflow_orchestration_adapter`
- `workflow_service`

## Integrations

- ChromaDB (RAG)
- Ollama (LLM)
- providers.base_provider
- providers.cloud_ollama_provider
- providers.local_ollama_provider
- providers.ollama_client
- providers.orchestrator_provider_factory

## Help Content (help/)

- `help/control_center/` — 6 articles
- `help/getting_started/` — 1 articles
- `help/operations/` — 9 articles
- `help/qa_governance/` — 1 articles
- `help/runtime_debug/` — 1 articles
- `help/settings/` — 4 articles
- `help/troubleshooting/` — 1 articles

## Help Topics

- `help/README.md`
- `help/control_center/cc_data_stores.md`
- `help/control_center/cc_models.md`
- `help/control_center/cc_providers.md`
- `help/control_center/cc_tools.md`
- `help/control_center/control_center_agents.md`
- `help/control_center/control_center_overview.md`
- `help/getting_started/introduction.md`
- `help/operations/agents_overview.md`
- `help/operations/chat_overview.md`
- `help/operations/deployment_workspace.md`
- `help/operations/knowledge_overview.md`
- `help/operations/operations_betrieb.md`
- `help/operations/projects_overview.md`
- `help/operations/prompt_studio_overview.md`
- `help/operations/scheduling_workflows.md`
- `help/operations/workflows_workspace.md`
- `help/qa_governance/qa_overview.md`
- `help/runtime_debug/runtime_overview.md`
- `help/settings/settings_chat_context.md`
- `help/settings/settings_overview.md`
- `help/settings/settings_prompts.md`
- `help/settings/settings_rag.md`
- `help/troubleshooting/troubleshooting.md`

## Test Suites

- `tests/unit/` — 215 test modules
- `tests/architecture/` — 66 test modules
- `tests/smoke/` — 39 test modules
- `tests/qa/` — 36 test modules
- `tests/contracts/` — 34 test modules
- `tests/ui/` — 19 test modules
- `tests/context/` — 18 test modules
- `tests/chat/` — 14 test modules
- `tests/failure_modes/` — 12 test modules
- `tests/integration/` — 10 test modules
- `tests/global_overlay/` — 7 test modules
- `tests/golden_path/` — 7 test modules
- `tests/tools/` — 7 test modules
- `tests/async_behavior/` — 6 test modules
- `tests/regression/` — 5 test modules
- `tests/ui_runtime/` — 5 test modules
- `tests/workspace_presets/` — 5 test modules
- `tests/chaos/` — 4 test modules
- `tests/scripts/` — 4 test modules
- `tests/structure/` — 4 test modules
- `tests/live/` — 3 test modules
- `tests/state_consistency/` — 3 test modules
- `tests/cli/` — 2 test modules
- `tests/cross_layer/` — 2 test modules
- `tests/helpers/` — 2 test modules
- `tests/meta/` — 2 test modules
- `tests/startup/` — 2 test modules
- `tests/gui/` — 1 test modules
- `tests/qml_agents/` — 1 test modules
- `tests/qml_chat/` — 1 test modules
- `tests/qml_deployment/` — 1 test modules
- `tests/qml_operations/` — 1 test modules
- `tests/qml_projects/` — 1 test modules
- `tests/qml_prompt_studio/` — 1 test modules
- `tests/qml_settings/` — 1 test modules
- `tests/qml_workflows/` — 1 test modules
