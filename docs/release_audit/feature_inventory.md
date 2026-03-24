# Feature inventory — Linux Desktop Chat

**Scope:** User-visible and product-level capabilities as named in `docs/FEATURE_REGISTRY.md` (auto-generated index) and the narrative list in `docs/00_map_of_the_system.md`. Service and help keys are copied from the registry where present.

---

## 1. Operations (main work areas)

| Feature (registry title) | Workspace ID | Primary code (registry) | Services (registry) | Help key (registry) |
|--------------------------|--------------|-------------------------|---------------------|---------------------|
| Chat | `operations_chat` | `app/gui/domains/operations/chat/chat_workspace.py` | `chat_service`, `llm`, `model_service`, `provider_service` | `chat_overview` |
| Knowledge | `operations_knowledge` | `app/gui/domains/operations/knowledge/knowledge_workspace.py` | `knowledge_service`, `rag` | `knowledge_overview` |
| Prompt Studio | `operations_prompt_studio` | `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` | `prompts`, `topic_service` | `prompt_studio_overview` |
| Workflows | `operations_workflows` | `app/gui/domains/operations/workflows/workflow_workspace.py` | `workflow_service`, `schedule_service`, `workflows` | `workflows_workspace` |
| Deployment | `operations_deployment` | `app/gui/domains/operations/deployment/deployment_workspace.py` | `deployment_operations_service` | `deployment_workspace` |
| Betrieb | `operations_audit_incidents` | `app/gui/domains/operations/audit_incidents/audit_incidents_workspace.py` | `audit_service`, `incident_service`, `platform_health_service` | `operations_betrieb` |
| Agent Tasks | `operations_agent_tasks` | `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` | `agent_service`, `agents` | `agents_overview` |
| Projects | `operations_projects` | `app/gui/domains/operations/projects/projects_workspace.py` | `project_service` | `projects_overview` |

`docs/00_map_of_the_system.md` additionally describes an **Operations** grouping and notes **Geplant** (scheduling) under Workflows.

---

## 2. Control Center

| Feature | Workspace ID | Primary code | Services | Help key |
|---------|--------------|--------------|----------|----------|
| Models | `cc_models` | `app/gui/domains/control_center/workspaces/models_workspace.py` | `model_service`, `provider_service` | `cc_models` |
| Providers | `cc_providers` | `app/gui/domains/control_center/workspaces/providers_workspace.py` | `provider_service` | `cc_providers` |
| Agents | `cc_agents` | `app/gui/domains/control_center/workspaces/agents_workspace.py` | `agent_service`, `agents` | `control_center_agents` |
| Tools | `cc_tools` | `app/gui/domains/control_center/workspaces/tools_workspace.py` | — | `cc_tools` |
| Data Stores | `cc_data_stores` | `app/gui/domains/control_center/workspaces/data_stores_workspace.py` | `rag` | `cc_data_stores` |

---

## 3. QA and governance

| Feature | Workspace ID | Primary code | Services | Help key |
|---------|--------------|--------------|----------|----------|
| Test Inventory | `qa_test_inventory` | `app/gui/domains/qa_governance/workspaces/test_inventory_workspace.py` | `qa_governance_service` | `qa_overview` |
| Coverage Map | `qa_coverage_map` | `app/gui/domains/qa_governance/workspaces/coverage_map_workspace.py` | `qa_governance_service` | — |
| Gap Analysis | `qa_gap_analysis` | `app/gui/domains/qa_governance/workspaces/gap_analysis_workspace.py` | `qa_governance_service` | — |
| Incidents | `qa_incidents` | `app/gui/domains/qa_governance/workspaces/incidents_workspace.py` | `qa_governance_service` | — |
| Replay Lab | `qa_replay_lab` | `app/gui/domains/qa_governance/workspaces/replay_lab_workspace.py` | `qa_governance_service` | — |

---

## 4. Runtime / debug

| Feature | Workspace ID | Primary code | Services | Help key |
|---------|--------------|--------------|----------|----------|
| EventBus | `rd_eventbus` | `app/gui/domains/runtime_debug/workspaces/eventbus_workspace.py` | — | — |
| Logs | `rd_logs` | `app/gui/domains/runtime_debug/workspaces/logs_workspace.py` | — | `runtime_overview` |
| Metrics | `rd_metrics` | `app/gui/domains/runtime_debug/workspaces/metrics_workspace.py` | — | — |
| LLM Calls | `rd_llm_calls` | `app/gui/domains/runtime_debug/workspaces/llm_calls_workspace.py` | — | — |
| Agent Activity | `rd_agent_activity` | `app/gui/domains/runtime_debug/workspaces/agent_activity_workspace.py` | `agent_service` | — |
| System Graph | `rd_system_graph` | `app/gui/domains/runtime_debug/workspaces/system_graph_workspace.py` | — | — |

---

## 5. Settings

| Feature | Workspace ID | Primary code (registry) | Services | Help key |
|---------|--------------|---------------------------|----------|----------|
| Application | `settings_application` | `app/gui/domains/settings/categories/application_category.py`, `…/workspaces/system_workspace.py` | `infrastructure` | `settings_chat_context` |
| Appearance | `settings_appearance` | `…/appearance_category.py`, `…/appearance_workspace.py` | — | `settings_overview` |
| AI / Models | `settings_ai_models` | `…/ai_models_category.py`, `…/workspaces/models_workspace.py` | `model_service`, `provider_service` | — |
| Data | `settings_data` | `…/data_category.py` | `rag` | — |
| Privacy | `settings_privacy` | `…/privacy_category.py` | — | — |
| Advanced | `settings_advanced` | `…/advanced_category.py`, `…/advanced_workspace.py` | — | — |
| Project | `settings_project` | `…/project_category.py` | `project_service` | — |
| Workspace | `settings_workspace` | `…/workspace_category.py` | — | — |

---

## 6. Shell-level UI (from `docs/00_map_of_the_system.md` only)

- **Command Center** / **Kommandozentrale** — dashboard-style shell area (`app/gui/domains/command_center/`, `dashboard/` exist in tree).
- **Sidebar navigation** — described in §4 of that document (German labels listed there).

---

## 7. Related product docs (pointers)

- `help/` — markdown help articles keyed by registry “Help” column where set.
- `docs/FEATURES/` — feature-oriented documentation folder present in repo.
- `docs/qa/` — QA architecture and artifact documentation referenced by registry “QA docs” rows for governance features.
