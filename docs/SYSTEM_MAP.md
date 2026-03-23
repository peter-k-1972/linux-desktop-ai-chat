# System Map – Linux Desktop Chat

*Auto-generated: 2026-03-20 20:57*

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
  app/chat/
  app/chats/
  app/cli/
  app/commands/
  app/context/
  app/core/
  app/critic.py
  app/db.py
  app/debug/
  app/gui/
  app/gui_designer_dummy/
  app/help/
  app/llm/
  app/main.py
  app/metrics/
  app/models/
  app/ollama_client.py
  app/pipelines/
  app/projects/
  app/prompts/
  app/providers/
  app/qa/
  app/rag/
  app/resources/
  app/resources_rc.py
  app/runtime/
  app/services/
  app/tools/
  app/utils/
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
-   Workspace: ChatWorkspace (chat)
-   Workspace: KnowledgeWorkspace (knowledge)
-   Workspace: ProjectsWorkspace (projects)
-   Workspace: PromptStudioWorkspace (prompt_studio)

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

- `agent_service`
- `agents`
- `chat_service`
- `context_explain_service`
- `context_inspection_service`
- `infrastructure`
- `knowledge_service`
- `llm`
- `model_service`
- `pipeline_service`
- `project_service`
- `prompts`
- `provider_service`
- `qa_governance_service`
- `rag`
- `result`
- `topic_service`

## Integrations

- ChromaDB (RAG)
- Ollama (LLM)
- providers.base_provider
- providers.cloud_ollama_provider
- providers.local_ollama_provider
- providers.ollama_client

## Help Content (help/)

- `help/control_center/` — 6 articles
- `help/getting_started/` — 1 articles
- `help/operations/` — 5 articles
- `help/qa_governance/` — 1 articles
- `help/runtime_debug/` — 1 articles
- `help/settings/` — 3 articles
- `help/troubleshooting/` — 1 articles

## Help Topics

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

## Test Suites

- `tests/qa/` — 36 test modules
- `tests/architecture/` — 17 test modules
- `tests/context/` — 17 test modules
- `tests/chat/` — 14 test modules
- `tests/unit/` — 14 test modules
- `tests/ui/` — 13 test modules
- `tests/failure_modes/` — 12 test modules
- `tests/contracts/` — 8 test modules
- `tests/integration/` — 8 test modules
- `tests/smoke/` — 8 test modules
- `tests/golden_path/` — 7 test modules
- `tests/async_behavior/` — 6 test modules
- `tests/regression/` — 5 test modules
- `tests/chaos/` — 4 test modules
- `tests/structure/` — 4 test modules
- `tests/live/` — 3 test modules
- `tests/state_consistency/` — 3 test modules
- `tests/cli/` — 2 test modules
- `tests/cross_layer/` — 2 test modules
- `tests/helpers/` — 2 test modules
- `tests/meta/` — 2 test modules
- `tests/startup/` — 2 test modules
- `tests/scripts/` — 1 test modules
