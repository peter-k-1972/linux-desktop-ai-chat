# Module map — Linux Desktop Chat

**Scope:** Inventory of modules by architectural role. Paths are under repository root unless noted. Counts are from `find … -name '*.py'` where stated.

---

## 1. Core (`app/core/`)

Subpackages present:

`audit`, `chat_guard`, `commands`, `config`, `context`, `db`, `deployment`, `llm`, `models` (includes `local_assets/`, `usage/`), `navigation`.

---

## 2. Services (`app/services/`)

**Count:** 41 Python files (including `__init__.py`).

**Modules (basename list):**  
`agent_operations_read_service.py`, `agent_service.py`, `audit_service.py`, `chat_service.py`, `context_explain_service.py`, `context_inspection_service.py`, `deployment_operations_service.py`, `doc_search_service.py`, `incident_service.py`, `infrastructure.py`, `infrastructure_snapshot.py`, `knowledge_service.py`, `local_model_asset_classifier.py`, `local_model_default_roots.py`, `local_model_matcher.py`, `local_model_registry_service.py`, `local_model_scanner_service.py`, `model_chat_runtime.py`, `model_invocation_display.py`, `model_orchestrator_service.py`, `model_quota_service.py`, `model_service.py`, `model_usage_aggregation_service.py`, `model_usage_gui_service.py`, `model_usage_service.py`, `pipeline_service.py`, `platform_health_service.py`, `project_service.py`, `provider_service.py`, `provider_usage_normalizer.py`, `qa_governance_service.py`, `result.py`, `schedule_service.py`, `token_usage_estimation.py`, `topic_service.py`, `unified_model_catalog_service.py`, `workflow_agent_adapter.py`, `workflow_context_adapter.py`, `workflow_orchestration_adapter.py`, `workflow_service.py`.

`app/services/__init__.py` explicitly documents: Chat, Model, Provider, Knowledge, Agent, Topic, Project, QA Governance, Pipeline accessors.

---

## 3. GUI (`app/gui/`)

**Domains** (see `system_inventory.md` §2).

**Monitors** (`app/gui/monitors/`):  
`metrics_monitor.py`, `agent_activity_monitor.py`, `bottom_panel_host.py`, `llm_trace_monitor.py`, `events_monitor.py`, `logs_monitor.py`, `__init__.py`.

**Legacy UI widgets** (`app/gui/legacy/`):  
`sidebar_widget.py`, `project_chat_list_widget.py`, `file_explorer_widget.py`, `chat_widget.py`, `message_widget.py`, `__init__.py`.

There is **no** top-level `app/ui/` Python package; GUI code lives under `app/gui/`.

---

## 4. Ports (`app/ui_application/ports/`)

| File |
|------|
| `agent_tasks_registry_port.py` |
| `agent_tasks_runtime_port.py` |
| `ai_model_catalog_port.py` |
| `chat_operations_port.py` |
| `deployment_releases_port.py` |
| `deployment_rollouts_port.py` |
| `deployment_targets_port.py` |
| `model_usage_gui_port.py` |
| `ollama_provider_settings_port.py` |
| `prompt_studio_port.py` |
| `settings_operations_port.py` |
| `settings_project_overview_port.py` |

---

## 5. Adapters (`app/ui_application/adapters/`)

| File |
|------|
| `service_agent_tasks_registry_adapter.py` |
| `service_agent_tasks_runtime_adapter.py` |
| `service_ai_model_catalog_adapter.py` |
| `service_chat_port_adapter.py` |
| `service_deployment_releases_adapter.py` |
| `service_deployment_rollouts_adapter.py` |
| `service_deployment_targets_adapter.py` |
| `service_model_usage_gui_adapter.py` |
| `service_ollama_provider_settings_adapter.py` |
| `service_prompt_studio_adapter.py` |
| `service_settings_adapter.py` |
| `service_settings_project_overview_adapter.py` |

---

## 6. Presenters (`app/ui_application/presenters/`)

| File |
|------|
| `agent_tasks_inspector_presenter.py` |
| `agent_tasks_registry_presenter.py` |
| `agent_tasks_runtime_presenter.py` |
| `agent_tasks_selection_presenter.py` |
| `agent_tasks_task_panel_presenter.py` |
| `base_presenter.py` |
| `chat_presenter.py` |
| `chat_send_callbacks.py` |
| `chat_stream_assembler.py` |
| `deployment_releases_presenter.py` |
| `deployment_rollouts_presenter.py` |
| `deployment_targets_presenter.py` |
| `model_usage_sidebar_presenter.py` |
| `prompt_studio_detail_presenter.py` |
| `prompt_studio_editor_presenter.py` |
| `prompt_studio_list_presenter.py` |
| `prompt_studio_templates_presenter.py` |
| `prompt_studio_test_lab_presenter.py` |
| `prompt_studio_versions_presenter.py` |
| `prompt_studio_workspace_presenter.py` |
| `settings_advanced_presenter.py` |
| `settings_ai_model_catalog_presenter.py` |
| `settings_ai_models_presenter.py` |
| `settings_appearance_presenter.py` |
| `settings_data_presenter.py` |
| `settings_legacy_modal_presenter.py` |
| `settings_model_routing_presenter.py` |
| `settings_project_overview_presenter.py` |

**Supporting:** `app/ui_application/presenter_base.py`, `app/ui_application/mappers/chat_mapper.py`, `chat_details_mapper.py`, `app/ui_application/view_models/protocols.py`.

---

## 7. UI contracts (`app/ui_contracts/workspaces/`)

Python modules:  
`agent_tasks_inspector.py`, `agent_tasks_registry.py`, `agent_tasks_runtime.py`, `agent_tasks_task_panel.py`, `chat.py`, `deployment_releases.py`, `deployment_rollouts.py`, `deployment_targets.py`, `model_usage_sidebar.py`, `prompt_studio_detail.py`, `prompt_studio_editor.py`, `prompt_studio_library.py`, `prompt_studio_list.py`, `prompt_studio_templates.py`, `prompt_studio_test_lab.py`, `prompt_studio_versions.py`, `prompt_studio_workspace.py`, `settings_advanced.py`, `settings_ai_model_catalog.py`, `settings_ai_models.py`, `settings_appearance.py`, `settings_data.py`, `settings_legacy_modal.py`, `settings_modal_ollama.py`, `settings_model_routing.py`, `settings_project_overview.py`, plus `common/` and package `__init__.py` files.

---

## 8. Other notable packages

| Package | Contents (high level) |
|---------|------------------------|
| `app/providers/` | `base_provider.py`, `local_ollama_provider.py`, `cloud_ollama_provider.py`, `ollama_client.py` |
| `app/workflows/` | `execution/` (incl. `node_executors/`), `models/`, `persistence/`, `queries/`, `registry/`, `scheduling/`, `serialization/`, `validation/` |
| `app/pipelines/` | `engine/`, `executors/`, `models/`, `registry/`, `services/` |
| `app/persistence/` | `orm/` and related persistence code |
| `app/context/` | `explainability/`, `inspection/`, `replay/`, `debug/`, `devtools/` |
| `app/qa/` | `operations_models.py`, `drilldown_models.py`, `operations_adapter.py`, `dashboard_adapter.py`, `__init__.py` |
| `app/rag/` | RAG pipeline support modules |
| `app/agents/` | Agent subsystem; includes `farm/` (catalog loader + JSON) |
| `app/cli/` | CLI entrypoints (e.g. context replay tooling referenced by tests) |
| `app/ui_runtime/` | `base_runtime.py`, `command_dispatcher.py`, `panel_wiring.py`, `manifest_models.py`, `theme_loader.py`, `theme_registry.py`, `qml/qml_runtime.py`, `widgets/widgets_runtime.py` |
