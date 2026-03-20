# Architecture Map

**Projekt:** Linux Desktop Chat  
**Generiert:** 2026-03-17T02:13:22Z  
**Status:** Governance gehärtet, Baseline 2026

---

## 1. Executive Summary

- Projekt: Linux Desktop Chat
- Generierungszeitpunkt: 2026-03-17T02:13:22Z
- Statushinweis: Governance gehärtet, Baseline 2026

---

## 2. Layers

| Schicht | Pfad | Rolle |
|---------|------|-------|
| GUI | app/gui/ | Shell, Domains, Workspace, Navigation, Commands, Inspector |
| Services | app/services/ | Chat, Model, Provider, Knowledge, Agent, Project, Topic, QA-Governance, Infrastructure |
| Providers | app/providers/ | LocalOllamaProvider, CloudOllamaProvider |
| Core | app/core/ | Models, Navigation, Context, DB, Commands, LLM, Config |

---

## 3. Domains

| Domäne | Pfad | Rolle |
|--------|------|-------|
| agents | app/agents/ | AgentProfile, Registry, Repository, TaskRunner |
| rag | app/rag/ | Retriever, Embedding, Service, VectorStore |
| tools | app/tools/ | FileSystemTools, web_search (keine Registry) |
| debug | app/debug/ | Emitter, EventBus, DebugStore, AgentEvent |
| metrics | app/metrics/ | MetricsCollector, Agent-Metriken |
| qa | app/qa/ | Operations-Adapter, Dashboard-Adapter |
| prompts | app/prompts/ | Prompt-Modelle, Service, Repository |
| utils | app/utils/ | Env-Loader, Datetime (nur stdlib) |

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

**Tools:** app/tools/ listet explizit; bewusste Entscheidung (TOOLS_GOVERNANCE_DECISION.md)

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
- **Temporär erlaubt (app/ Root):** critic.py, db.py, ollama_client.py
- **Verboten (Parallelstrukturen):** ui

---

*Quelle: arch_guard_config, ARCHITECTURE_BASELINE_2026. Generiert von scripts/dev/architecture_map.py*
