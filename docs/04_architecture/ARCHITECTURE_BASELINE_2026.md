# Architektur-Baseline 2026

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Offizielle Referenz nach Governance-Härtung

---

## A. Executive Summary

**Gesamtstatus:** Architektonisch stabil, governance-seitig gehärtet.

**Reifegrad:** Vollständige Layer-Trennung, 11 Governance-Blöcke mit pytest-Guards, Architecture Drift Radar operativ. Bewusste Restpunkte dokumentiert.

**Baseline-Zweck:** Referenz für Refactors, Reviews, Governance-Checks und Featurearbeiten. Abweichungen von dieser Baseline gelten als Drift.

---

## B. Systemstruktur

### Hauptschichten

| Schicht | Pfad | Rolle |
|---------|------|-------|
| **GUI** | app/gui/ | Shell, Domains, Workspace, Navigation, Commands, Inspector, Monitors. Qt-basiert. |
| **Services** | app/services/ | Chat, Model, Provider, Knowledge, Agent, Project, Topic, QA-Governance, Infrastructure. |
| **Providers** | app/providers/ | LocalOllamaProvider, CloudOllamaProvider. Keine GUI-Imports. |
| **Core** | app/core/ | Models (Registry, Orchestrator), Navigation, Context, DB, Commands, LLM, Config. |

### Weitere Domänen

| Domäne | Pfad | Rolle |
|--------|------|-------|
| **agents** | app/agents/ | AgentProfile, Registry, Repository, TaskRunner, Orchestration. |
| **tools** | app/tools/ | FileSystemTools, web_search. Keine formale Registry (bewusste Entscheidung). |
| **rag** | app/rag/ | Retriever, Embedding, Service, VectorStore, Knowledge-Extraktion. |
| **debug** | app/debug/ | Emitter, EventBus, DebugStore, AgentEvent. |
| **metrics** | app/metrics/ | MetricsCollector, Agent-Metriken. |
| **qa** | app/qa/ | Operations-Adapter, Dashboard-Adapter, DTOs. |
| **prompts** | app/prompts/ | Prompt-Modelle, Service, Repository. |
| **utils** | app/utils/ | Env-Loader, Datetime. Nur stdlib; keine app.*-Imports. |

---

## C. Architekturregeln

### Erlaubte Abhängigkeitsrichtungen

- GUI → Services, Core (Models, Navigation), Debug (lesend über get_debug_store)
- Services → Core, Providers (nur über Infrastructure/OllamaClient), Debug (lesend)
- Core → keine GUI, Services, Providers, Agents, RAG, Debug, Metrics
- Providers → Core (nur Models/Orchestrator), keine GUI
- Agents, RAG → Debug (emit_event)
- Utils → nur stdlib

### Verbotene Kopplungen (FORBIDDEN_IMPORT_RULES)

| Quelle | Darf NICHT importieren |
|--------|------------------------|
| core | gui, agents, rag, prompts, providers, services, debug, metrics |
| utils | core, gui, agents, rag, prompts, providers, services, debug, metrics, tools |
| providers | gui, agents, rag, prompts, services, debug, metrics |
| services | gui |
| gui | providers |
| tools, metrics, debug | gui, agents, rag, prompts, providers, services |

### Zentrale Layer-Regeln

1. **services → gui:** Verboten. Services kennen keine GUI.
2. **gui → providers:** Verboten. GUI nutzt ModelService, ProviderService.
3. **core:** Bleibt schlank; keine Domänen-Logik.
4. **FORBIDDEN_PARALLEL_PACKAGES:** app/ui darf nicht neu erstellt werden (migriert nach gui).

### Bekannte Import-Ausnahmen (KNOWN_IMPORT_EXCEPTIONS)

- core/llm/llm_complete.py → debug (emit_event)
- core/context/project_context_manager.py → services, gui (Projekt-Load, Events)
- core/models/orchestrator.py → providers (Provider-Zuordnung)
- metrics/metrics_collector.py → debug (EventBus)
- main.py → providers (Legacy)
- ollama_client.py → providers (Root-Re-Export)

*(settings_dialog nutzt ModelService/ProviderService – entkoppelt, keine Ausnahme mehr)*

---

## D. Kanonische Einstiegspunkte

| Einstiegspunkt | Pfad | Typ | Delegation |
|----------------|------|-----|------------|
| **Standard-GUI** | run_gui_shell.py | Kanonisch | — |
| **Standard-GUI** | app/__main__.py | Kanonisch | → run_gui_shell.main |
| **Standard-GUI** | main.py (Root) | Kanonisch | → run_gui_shell.main |
| **Legacy-GUI** | archive/run_legacy_gui.py | Legacy | → app.main.main |

### Bootstrap-Contract

Jeder kanonische GUI-Einstiegspunkt muss in main() enthalten:
- `init_infrastructure`
- `create_qsettings_backend`

### Legacy-Pfade

- **app.main:** Nur für archive/run_legacy_gui. Direkte Provider-Verdrahtung. Siehe LEGACY_MAIN_GOVERNANCE.md.
- **app.__main__:** Delegiert an run_gui_shell, nicht an app.main.

---

## E. Startup-/Bootstrap-Baseline

### Reihenfolge (run_gui_shell)

1. load_env()
2. install_gui_log_handler()
3. get_metrics_collector()
4. QApplication(sys.argv)
5. qasync QEventLoop
6. **init_infrastructure(settings_backend=create_qsettings_backend())**
7. get_infrastructure()
8. set_chat_backend(), set_knowledge_backend()
9. get_theme_manager().set_theme()
10. ShellMainWindow() → register_all_screens(), register_commands(), load_all_palette_commands()

### Settings-Backend-Injektion

- **Produktive GUI:** create_qsettings_backend() vor init_infrastructure
- **Tests:** InMemoryBackend oder set_infrastructure(mock)
- **Kein stiller Fallback:** Produktive GUI darf nicht mit InMemoryBackend starten

### Regeln gegen Frühzugriff

- GUI-Module dürfen bei Import-Zeit kein get_infrastructure(), get_chat_service() etc. aufrufen
- Materialisierung lazy in Methoden/Callbacks

---

## F. Registry-Baseline

| Registry | Ort | Registrierung | Lifecycle |
|----------|-----|---------------|-----------|
| **Model Registry** | core/models/registry.py | _load_defaults(), register() | Statisch |
| **Navigation Registry** | core/navigation/navigation_registry.py | _build_registry() | Statisch |
| **Screen Registry** | gui/workspace/screen_registry, gui/bootstrap | register_all_screens() | Einmal bei Bootstrap |
| **Command Registry** | gui/commands/registry, bootstrap, palette_loader | register_commands(), load_all_palette_commands() | Bei Bootstrap |
| **Agent Registry** | agents/agent_registry.py | register_profile(), seed_agents | Lazy |

### Bewusst keine Registry

- **Tools:** app/tools/__init__.py listet explizit. Siehe TOOLS_GOVERNANCE_DECISION.md.

---

## G. Provider-/Modellorchestrierung

### ModelRegistry

- Provider-Strings: `local`, `ollama_cloud` (KNOWN_MODEL_PROVIDER_STRINGS)
- ModelEntry.provider muss in KNOWN_MODEL_PROVIDER_STRINGS liegen

### Provider-Auflösung

- **Einziger Auflösungsort:** core/models/orchestrator.py → get_provider_for_model(model_id)
- **Verdrahtung:** app.main (Legacy) instanziiert LocalOllamaProvider, CloudOllamaProvider → ModelOrchestrator
- **Standard-GUI:** Nutzt ChatBackend, KnowledgeBackend; keine direkte Provider-Verdrahtung

### Erlaubte Resolver-Pfade

- ALLOWED_PROVIDER_STRING_FILES: registry.py, local_ollama_provider, cloud_ollama_provider, arch_guard_config, Tests
- Keine weiteren Orte für Provider-Strings

### Einschränkungen

- GUI nutzt ModelService, ProviderService; keine Provider-Imports (außer main.py Legacy)
- Services nutzen Infrastructure (OllamaClient), nicht Provider-Klassen direkt

---

## H. EventBus-/Observability-Baseline

### Event-System

- **EventType:** app/debug/agent_event.py
- **Emitter:** app/debug/emitter.emit_event()
- **EventBus:** app/debug/event_bus.get_event_bus()

### Erlaubte Publisher (emit_event)

- app/agents/
- app/rag/
- app/core/llm/llm_complete.py
- app/gui/legacy/chat_widget.py

### Erlaubte EventBus-Direktimporter

- app/debug/
- app/agents/agent_task_runner.py
- app/metrics/metrics_collector.py

### Verboten

- providers, prompts, tools, utils dürfen app.debug (EventBus, emit_event) nicht importieren

### Debug/Metrics-Grenzen

- GUI liest über get_debug_store(); kein direkter subscribe()
- Metrics: EventBus-Subscriber für Metrik-Aggregation

---

## I. Governance-Blöcke

| Block | Policy | Guard/Test | Absichert |
|-------|--------|------------|-----------|
| GUI Governance | GUI_GOVERNANCE_POLICY | test_gui_governance_guards | Screen/Workspace-Map, NavAreas, Commands |
| GUI Domain Dependency | GUI_DOMAIN_DEPENDENCY_POLICY | test_gui_domain_dependency_guards | Domain-zu-Domain-Imports |
| Service Governance | SERVICE_GOVERNANCE_POLICY | test_service_governance_guards | services→gui, gui→providers |
| Startup Governance | STARTUP_GOVERNANCE_POLICY | test_startup_governance_guards | Entrypoints, Bootstrap-Contract |
| Registry Governance | REGISTRY_GOVERNANCE_POLICY | test_registry_governance_guards | Model, Nav, Screen, Command |
| Provider Orchestrator | PROVIDER_ORCHESTRATOR_GOVERNANCE | test_provider_orchestrator_guards | Provider-Strings, Hardcoding |
| EventBus Governance | EVENTBUS_GOVERNANCE_POLICY | test_eventbus_governance_guards | emit_event, get_event_bus |
| Feature Governance | FEATURE_GOVERNANCE_POLICY | test_feature_governance_guards | Feature-Registry-Konsistenz |
| App Package | APP_TARGET_PACKAGE_ARCHITECTURE | test_app_package_guards | Root-Dateien, Target-Packages |
| Architecture Drift Radar | ARCHITECTURE_DRIFT_RADAR_POLICY | test_architecture_drift_radar | Konsolidierter Report |
| gui does not import ui | ARCHITECTURE_GUARD_RULES | test_gui_does_not_import_ui | gui→ui Verbot |

**Zentrale Konfiguration:** tests/architecture/arch_guard_config.py

---

## J. Drift-Radar-Bezug

### Überwachte Drift-Arten

| Kategorie | Beschreibung |
|-----------|--------------|
| layer_drift | FORBIDDEN_IMPORT_RULES-Verletzung |
| startup_drift | Bootstrap/Entrypoint-Abweichung |
| registry_drift | Registry-Inkonsistenz |
| provider_drift | Provider-String/Orchestrator-Drift |
| event_drift | EventBus-Drift |
| entrypoint_drift | Neue unerlaubte Einstiegspunkte |
| hardcoding_drift | Unerlaubte Provider-Hardcodings |
| gui_domain_drift | GUI-Domain-Abhängigkeitsverletzung |
| feature_drift | Feature-Registry-Divergenz |

### Was als Drift gilt

Abweichung von dieser Baseline bzw. von arch_guard_config-Regeln. Schweregrade: critical, high, medium, low.

### Skript

`python scripts/architecture/architecture_drift_radar.py`  
Ausgabe: docs/04_architecture/ARCHITECTURE_DRIFT_RADAR.json, ARCHITECTURE_DRIFT_RADAR_STATUS.md

---

## K. Bewusste Restpunkte

| Restpunkt | Status | Referenz |
|-----------|--------|----------|
| **app.main Legacy** | Bewusst | LEGACY_MAIN_GOVERNANCE.md; nur für archive/run_legacy_gui |
| **TEMPORARILY_ALLOWED_ROOT_FILES** | db.py, critic.py, ollama_client.py | Phase D; APP_MOVE_MATRIX |
| **app/llm** | Re-Export von core/llm | LLM_MODULE_STRUCTURE.md |
| **Tools ohne Registry** | Bewusste Entscheidung | TOOLS_GOVERNANCE_DECISION.md |
| **KNOWN_GUI_DOMAIN_EXCEPTIONS** | chat_side_panel → settings, runtime_debug | 2 dokumentierte Ausnahmen |
| **test_gui_does_not_import_ui** | Sentinel (app.ui entfernt) | Guard gegen Drift |

---

## L. Freigabestatus

**Aktueller Status:** Freigabe für laufenden Betrieb. Architektur-Kern intakt, Governance-Blöcke operativ.

### Worauf zukünftige Änderungen achten müssen

1. **Neue Imports:** FORBIDDEN_IMPORT_RULES prüfen; KNOWN_IMPORT_EXCEPTIONS nur nach Review.
2. **Neue Einstiegspunkte:** Bootstrap-Contract erfüllen; CANONICAL_GUI_ENTRY_POINTS ggf. erweitern.
3. **Neue Provider:** KNOWN_MODEL_PROVIDER_STRINGS, ALLOWED_PROVIDER_STRING_FILES, Orchestrator anpassen.
4. **Neue Event-Publisher:** ALLOWED_EMIT_EVENT_IMPORTERS erweitern.
5. **GUI-Domain-Imports:** FORBIDDEN_GUI_DOMAIN_PAIRS prüfen.

### Bei größeren Refactors zuerst aktualisieren

- arch_guard_config.py
- Betroffene Policy-Dokumente (docs/04_architecture/)
- Architecture Drift Radar (falls neue Kategorien)
- pytest architecture-Guards

---

## Änderungspflicht bei Architekturänderungen

| Änderung | Aktualisieren |
|----------|---------------|
| Neue Layer/Package | FORBIDDEN_IMPORT_RULES, TARGET_PACKAGES, ggf. Policy |
| Neuer Einstiegspunkt | CANONICAL_GUI_ENTRY_POINTS, STARTUP_GOVERNANCE_POLICY |
| Neuer Provider-String | KNOWN_MODEL_PROVIDER_STRINGS, ALLOWED_PROVIDER_STRING_FILES, PROVIDER_ORCHESTRATOR_GOVERNANCE |
| Neue Registry | REGISTRY_GOVERNANCE_POLICY, test_registry_governance_guards |
| Neue Event-Publisher | ALLOWED_EMIT_EVENT_IMPORTERS, EVENTBUS_GOVERNANCE_POLICY |
| GUI-Screen/Workspace | GUI_SCREEN_WORKSPACE_MAP, GUI_GOVERNANCE_POLICY |
| GUI-Domain-Dependency | FORBIDDEN_GUI_DOMAIN_PAIRS, GUI_DOMAIN_DEPENDENCY_POLICY |
