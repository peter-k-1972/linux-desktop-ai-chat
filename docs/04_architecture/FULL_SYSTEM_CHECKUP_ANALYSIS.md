# Full System Checkup – Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17  
**Rolle:** Principal Software Architect, Governance Engineer, QA-Lead, System Reviewer

---

## 1. Analysierter Umfang

### 1.1 Verzeichnisstruktur

| Bereich | Pfad | Status |
|---------|------|--------|
| App-Paket | `app/` | Vollständig analysiert |
| Tests | `tests/` | architecture, qa, contracts, smoke, integration, chaos, startup |
| Architektur-Docs | `docs/04_architecture/` | Policies, Audits, Reports (kanonischer Pfad) |
| Architektur-Skripte | `scripts/architecture/` | architecture_drift_radar, architecture_health_check |
| QA-Skripte | `scripts/qa/` | build_test_inventory, coverage_map, feedback_loop, incidents, knowledge_graph |
| Bootstrap/Entrypoints | `main.py`, `run_gui_shell.py`, `app/__main__.py`, `start.sh` | Vollständig |
| Services | `app/services/` | 10 Service-Module inkl. pipeline_service (Facade) |
| Providers | `app/providers/` | local_ollama, cloud_ollama |
| Core | `app/core/` | models, navigation, context, db, commands, llm, config |
| GUI | `app/gui/` | shell, domains, workspace, navigation, commands, inspector, monitors |
| Agents | `app/agents/` | registry, repository, task_runner, orchestration |
| Tools | `app/tools/` | filesystem, web_search (bewusst ohne Registry) |
| RAG | `app/rag/` | retriever, embedding, service, vector_store |
| Debug/Observability | `app/debug/`, `app/metrics/` | emitter, event_bus, debug_store |
| Pipelines | `app/pipelines/` | engine, executors, registry, services |
| Archive | `archive/` | run_legacy_gui.py → app.main |

### 1.2 Entrypoint- und Bootstrap-Flow

```
main.py → run_gui_shell.main()
app/__main__.py → run_gui_shell.main()
start.sh → python -m app
archive/run_legacy_gui.py → app.main.main() [LEGACY]
```

**Bootstrap-Reihenfolge (run_gui_shell):**
1. load_env()
2. install_gui_log_handler()
3. get_metrics_collector()
4. try_acquire_single_instance_lock()
5. QApplication
6. qasync QEventLoop
7. init_infrastructure(create_qsettings_backend())
8. get_infrastructure()
9. set_chat_backend(), set_knowledge_backend()
10. get_theme_manager().set_theme()
11. ShellMainWindow() → register_all_screens(), register_commands(), load_all_palette_commands()

---

## 2. Technische Prüfbereiche

### A. Layer & Import Governance

**Konfiguration:** `arch_guard_config.FORBIDDEN_IMPORT_RULES`, `KNOWN_IMPORT_EXCEPTIONS`

| Regel | Status | Hinweise |
|-------|--------|----------|
| core → gui/services/providers | Guard aktiv | Bekannte Ausnahmen: project_context_manager (services, gui), orchestrator (providers) |
| services → gui | Guard aktiv | KEINE Ausnahmen (infrastructure behoben) |
| gui → providers | Guard aktiv | Nur main.py (Legacy); settings_dialog entkoppelt |
| utils → app.* | Guard aktiv | utils bleibt stdlib-only |
| providers → services/gui | Guard aktiv | |

**Potenzielle Zyklen:** Keine offensichtlichen Zyklen in der Importstruktur identifiziert.

**Versteckte GUI-Kopplungen (dokumentierte Ausnahmen):**
- `core/context/project_context_manager.py` → gui.events (emit_project_context_changed)
- `core/llm/llm_complete.py` → debug (emit_event)

**Core → help:** `core/navigation/help_topic_resolver.py` importiert `app.help.help_index`. help ist nicht in FORBIDDEN_IMPORT_RULES für core – aktuell erlaubt. Optional: Prüfen ob help als Feature-Package in Layer-Regeln aufgenommen werden soll.

### B. Startup & Lifecycle

| Aspekt | Status | Risiko |
|--------|--------|--------|
| Kanonische Entrypoints | run_gui_shell.py, app.main (Legacy) | app.main nur für archive |
| app.__main__ Delegation | Delegiert an run_gui_shell ✓ | Korrekt |
| init_infrastructure vor get_infrastructure | run_gui_shell ✓ | Korrekt |
| ShellMainWindow nach init | run_gui_shell ✓ | Korrekt |
| Single-Instance-Lock | try_acquire_single_instance_lock() | Lifecycle-Policy |
| Singleton/Global-State | get_infrastructure(), get_event_bus(), get_metrics_collector() | Bewusst; dokumentiert |

**Initialisierungsdrift:**
- app.main (Legacy) erfüllt Bootstrap-Contract (init_infrastructure, create_qsettings_backend)
- archive/run_legacy_gui.py delegiert an app.main

### C. Registry & Runtime Contracts

| Registry | Ort | Governance | Status |
|----------|-----|------------|--------|
| Model Registry | core/models/registry.py | REGISTRY_GOVERNANCE | Provider-Strings: local, ollama_cloud |
| Navigation Registry | core/navigation/navigation_registry.py | REGISTRY_GOVERNANCE | Statisch |
| Screen Registry | gui/workspace/screen_registry, gui/bootstrap | GUI_GOVERNANCE | register_all_screens() |
| Command Registry | gui/commands/registry, bootstrap, palette_loader | REGISTRY_GOVERNANCE | |
| Agent Registry | agents/agent_registry.py | Keine explizite Policy | Funktional; optional erweiterbar |
| Tools | tools/__init__.py | TOOLS_GOVERNANCE_DECISION | Bewusst keine Registry |
| Pipeline Definition Registry | pipelines/registry/definition_registry.py | PIPELINE_ENGINE_POLICY | |

### D. Provider & Modellorchestrierung

| Aspekt | Status |
|--------|--------|
| Erlaubte Provider-Strings | local, ollama_cloud (KNOWN_MODEL_PROVIDER_STRINGS) |
| ALLOWED_PROVIDER_STRING_FILES | registry.py, local_ollama_provider, cloud_ollama_provider, arch_guard_config, Tests |
| Harte Verdrahtung app.main | LocalOllamaProvider, CloudOllamaProvider → ModelOrchestrator (Legacy) |
| run_gui_shell | Nutzt ChatBackend, KnowledgeBackend – keine direkte Provider-Verdrahtung |
| Orchestrator | core/models/orchestrator.py – Provider-Zuordnung (dokumentierte Ausnahme) |
| settings_dialog | Nutzt ModelService, ProviderService – entkoppelt |

**Implizite Verträge:** Provider-Implementierungen müssen OllamaClient/API-Key bereitstellen; nicht formal spezifiziert.

### E. EventBus / Debug / Observability

| Komponente | Erlaubte Importer | Status |
|------------|-------------------|--------|
| emit_event | agents/, rag/, core/llm/llm_complete.py, gui/legacy/chat_widget | ALLOWED_EMIT_EVENT_IMPORTERS |
| get_event_bus | debug/, agents/agent_task_runner, metrics/metrics_collector | ALLOWED_EVENTBUS_DIRECT_IMPORTERS |
| FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES | providers, prompts, tools, utils | Guard aktiv |

**Event-Namensräume:** EventType in debug/agent_event.py; keine formale Namespace-Policy.

**Semantische Kopplung:** Event-Payload-Struktur nicht schema-validiert.

### F. Legacy / Orphans / Dead Structures

| Element | Status | Empfehlung |
|---------|--------|------------|
| app.main | Legacy, deprecated | Beibehalten bis archive/run_legacy_gui entfernt |
| app/ui | **Nicht mehr vorhanden** | FORBIDDEN_PARALLEL_PACKAGES verhindert Neuaufbau |
| archive/run_legacy_gui.py | Deprecated | Importiert app.main |
| app/ollama_client.py | Root-Re-Export | Re-export von app.providers.ollama_client |
| app/db.py, app/critic.py | TEMPORARILY_ALLOWED_ROOT_FILES | Phase D: verschieben |
| ROOT_LEGACY_MODULES | chat_widget, sidebar_widget, etc. | In gui/legacy migriert |
| docs/architecture | Redirect | README verweist auf docs/04_architecture |

**Verwaiste Dateien:** Keine offensichtlich verwaisten Produktivmodule identifiziert.

**Namenskonventionen:**
- `app/commands/` vs `app/core/commands/` – Re-Export-Pattern
- `app/llm/` vs `app/core/llm/` – Re-Export (LLM_MODULE_STRUCTURE.md)
- `app/services/pipeline_service.py` – Facade für app.pipelines.services

### G. Test- und Governance-Abdeckung

| Governance-Block | Test-Modul | Stärke | Lücken |
|------------------|------------|--------|--------|
| GUI | test_gui_governance_guards | Stark | Screen/Workspace-Map statisch |
| GUI Domain | test_gui_domain_dependency_guards | Stark | 2 dokumentierte Ausnahmen |
| Service | test_service_governance_guards | Stark | Keine |
| Startup | test_startup_governance_guards | Stark | Keine |
| Registry | test_registry_governance_guards | Stark | Keine |
| Provider Orchestrator | test_provider_orchestrator_governance_guards | Stark | Keine |
| EventBus | test_eventbus_governance_guards | Stark | Keine |
| Feature | test_feature_governance_guards | Mittel | Feature-Registry manuell |
| App Package | test_app_package_guards | Stark | TEMPORARILY_ALLOWED |
| Lifecycle | test_lifecycle_guards | Stark | Keine |
| Root Entrypoint | test_root_entrypoint_guards | Stark | Keine |
| Drift Radar | test_architecture_drift_radar | Stark | DOCS_ARCH = docs/04_architecture ✓ |
| gui does not import ui | test_gui_does_not_import_ui | Sentinel | Drift-Guard |

**Guards ohne echte Tests:** Keine – alle Guards haben pytest-Sentinel-Tests.

**Statisch vs. semantisch:** Import-Guards prüfen statisch (AST); semantische Verträge (z.B. Event-Payload) nicht automatisiert.

---

## 3. Pfad-Konsistenz (behoben)

**Status:** DOCS_ARCH zeigt auf `docs/04_architecture` in:
- arch_guard_config.py
- architecture_drift_radar.py
- architecture_health_check.py
- scripts/dev/architecture_map.py

**docs/architecture/:** Enthält README (Redirect) und ggf. Restpoint-Reports; kanonischer Inhalt in docs/04_architecture.

---

## 4. Doppelte Strukturen (app/llm vs app/core/llm)

- `app/llm/` – Re-Export-Layer für Rückwärtskompatibilität
- `app/core/llm/` – Kanonische Implementierung

Dokumentiert in LLM_MODULE_STRUCTURE.md. Keine Governance-Regelverletzung.

---

## 5. Pipeline-Architektur

- `app/pipelines/` – Engine, Executors, Registry, Models
- `app/services/pipeline_service.py` – Facade; GUI/Services nutzen get_pipeline_service()
- PIPELINE_ENGINE_POLICY, RUNTIME_LIFECYCLE_POLICY vorhanden

---

## 6. Architektur-Drift-Radar (aktuell)

**Stand 2026-03-17:**
- 93 Tests bestanden, 0 fehlgeschlagen
- Alle Governance-Dateien vorhanden (governance_files: true)
- Drift-Kategorien: layer, startup, registry, provider, event, entrypoint, hardcoding, gui_domain, feature – alle ok
