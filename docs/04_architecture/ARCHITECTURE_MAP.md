# Architecture Map

**Projekt:** Linux Desktop Chat  
**Generiert:** 2026-03-30T22:22:37Z  
**Status:** Governance gehärtet, Baseline 2026

---

## 1. Executive Summary

- Projekt: Linux Desktop Chat
- Generierungszeitpunkt: 2026-03-30T22:22:37Z
- Statushinweis: Governance gehärtet, Baseline 2026

---

## 2. Layers

| Schicht | Pfad | Rolle |
|---------|------|-------|
| GUI | app/gui/ | Shell, Domains, Workspace, Navigation, Commands, Inspector |
| Services | app/services/ | Chat, Model, Provider, Knowledge, Agent, Project, Topic, QA-Governance, Infrastructure |
| Providers | linux-desktop-chat-providers/src/app/providers/ | LocalOllamaProvider, CloudOllamaProvider (Import app.providers) |
| CLI | linux-desktop-chat-cli/src/app/cli/ | Context replay/repro/registry headless tools (Import app.cli) |
| Utils | linux-desktop-chat-utils/src/app/utils/ | Paths, datetime, env loader (Import app.utils) |
| UI themes (builtins) | linux-desktop-chat-ui-themes/src/app/ui_themes/ | Theme manifests/QSS/JSON (Import app.ui_themes) |
| UI runtime (QML/widgets) | linux-desktop-chat-ui-runtime/src/app/ui_runtime/ | Theme manifest validation, QmlRuntime, shell bridge (Import app.ui_runtime) |
| Product runtime | linux-desktop-chat-runtime/src/app/runtime/ | Single-instance lock, shutdown hooks, model_invocation DTOs (Import app.runtime); app.extensions discovery root |
| Core | app/core/ | Models, Navigation, Context, DB, Commands, LLM, Config |

---

## 3. Domains

| Domäne | Pfad | Rolle |
|--------|------|-------|
| agents | app/agents/ | AgentProfile, Registry, Repository, TaskRunner |
| rag | app/rag/ | Retriever, Embedding, Service, VectorStore |
| tools | linux-desktop-chat-infra/src/app/tools/ | FileSystemTools, web_search (keine Registry; Import app.tools) |
| debug | linux-desktop-chat-infra/src/app/debug/ | Emitter, EventBus, DebugStore, AgentEvent (Import app.debug) |
| metrics | linux-desktop-chat-infra/src/app/metrics/ | MetricsCollector, Agent-Metriken (Import app.metrics) |
| qa | app/qa/ | Operations-Adapter, Dashboard-Adapter |
| prompts | app/prompts/ | Prompt-Modelle, Service, Repository |
| utils | linux-desktop-chat-utils/src/app/utils/ | Paths, Env-Loader, Datetime (nur stdlib; Import app.utils) |

---

## 4. Canonical Entrypoints

### Kanonisch

| Befehl | Pfad | Delegation |
|--------|------|------------|
| python -m app | app/__main__.py | run_gui_shell.main |
| python run_gui_shell.py | run_gui_shell.py | — |
| python main.py | main.py | run_gui_shell.main |
| start.sh | start.sh | python -m app |

### Legacy

| Befehl | Pfad | Delegation |
|--------|------|------------|
| python archive/run_legacy_gui.py | archive/run_legacy_gui.py | app.main.main |

---

## 5. Registries

| Registry | Ort | Lifecycle |
|----------|-----|-----------|
| Model Registry | app/core/models/registry.py | Statisch |
| Navigation Registry | app/core/navigation/navigation_registry.py | Statisch |
| Screen Registry | app/gui/workspace/screen_registry, gui/bootstrap | Bootstrap |
| Command Registry | app/gui/commands/registry, palette_loader | Bootstrap |
| Agent Registry | app/agents/agent_registry.py | Lazy |

**Tools:** linux-desktop-chat-infra/src/app/tools/ listet explizit; bewusste Entscheidung (TOOLS_GOVERNANCE_DECISION.md)

---

## 6. Services

- agent_service
- chat_service
- infrastructure
- knowledge_service
- model_service
- pipeline_service
- project_service
- provider_service
- qa_governance_service
- topic_service

---

## 7. Providers

- **Provider-Strings:** local, ollama_cloud
- **Implementierungen:** LocalOllamaProvider, CloudOllamaProvider

---

## 8. Governance Blocks

| Block | Policy | Guard |
|-------|--------|-------|
| GUI Governance | GUI_GOVERNANCE_POLICY.md | test_gui_governance_guards |
| GUI Domain Dependency | GUI_DOMAIN_DEPENDENCY_POLICY.md | test_gui_domain_dependency_guards |
| Service Governance | SERVICE_GOVERNANCE_POLICY.md | test_service_governance_guards |
| Startup Governance | STARTUP_GOVERNANCE_POLICY.md | test_startup_governance_guards |
| Registry Governance | REGISTRY_GOVERNANCE_POLICY.md | test_registry_governance_guards |
| Provider Orchestrator | PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md | test_provider_orchestrator_governance_guards |
| EventBus Governance | EVENTBUS_GOVERNANCE_POLICY.md | test_eventbus_governance_guards |
| Feature Governance | FEATURE_GOVERNANCE_POLICY.md | test_feature_governance_guards |
| App Package | APP_TARGET_PACKAGE_ARCHITECTURE | test_app_package_guards |
| Architecture Drift Radar | ARCHITECTURE_DRIFT_RADAR_POLICY.md | test_architecture_drift_radar |
| Root Entrypoint | ROOT_ENTRYPOINT_POLICY.md | test_root_entrypoint_guards |
| Lifecycle | RUNTIME_LIFECYCLE_POLICY.md | test_lifecycle_guards |

---

## 9. Known Legacy / Transitional

- **app.main:** Legacy MainWindow; nur archive/run_legacy_gui.py
- **Temporär erlaubt (app/ Root):** application_release_info.py, critic.py, gui_smoke_constants.py, gui_smoke_harness.py, qml_alternative_gui_validator.py, qml_theme_governance.py
- **Verboten (Parallelstrukturen):** ui

---

*Quelle: arch_guard_config, ARCHITECTURE_BASELINE_2026. Generiert von scripts/dev/architecture_map.py*
